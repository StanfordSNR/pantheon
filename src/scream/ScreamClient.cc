#include <iostream>
#include <cstdlib>
#include <cstdint>
#include <poll.h>

#include "socket.hh"
#include "timestamp.hh"
#include "util.hh"

#include "ScreamTx.h"
#include "RtpQueue.h"
#include "VideoEnc.h"
#include "Packet.hh"
#include "Timerfd.hh"

using namespace std;

const uint32_t SSRC = 10; /* arbitrary synchronization source id of stream */
const uint64_t tmax_ms = 75000; /* run 75 seconds */
bool debug = false;

/* Video encoder "encodes" new frames and updates target bitrate */
void encodeVideoFrame(VideoEnc *videoEnc, ScreamTx *screamTx)
{
  float targetBitrate = screamTx->getTargetBitrate(SSRC);
  videoEnc->setTargetBitrate(targetBitrate);

  /* encode(time) accepts time as seconds */
  int rtpBytes = videoEnc->encode((float) timestamp_ms() / 1000);
  screamTx->newMediaFrame(timestamp_ms() * 1000, SSRC, rtpBytes);
}

/* Check if client can send RTP packets now */
void sendRtp(ScreamTx *screamTx, RtpQueue *rtpQueue,
             Timerfd &txTimer, UDPSocket &socket)
{
  uint32_t ssrc; /* will be filled in with the SSRC of prioritized stream */
  float dT = screamTx->isOkToTransmit(timestamp_ms() * 1000, ssrc);

  /* RTP packet with ssrc can be immediately transmitted */
  if (dT == 0.0f) {
    void *rtpPacketNull = NULL; /* won't be filled in by API */
    int size;
    uint16_t seqNr;
    rtpQueue->sendPacket(rtpPacketNull, size, seqNr);

    /* Create RTP packet with dummy payload of size `size` */
    RtpPacket rtpPacket(ssrc, (uint32_t) size, seqNr);
    socket.send(rtpPacket.to_string());

    if (debug) {
      cerr << "Sent a RTP packet of size " << rtpPacket.payload.size()
           << " with sequence number " << seqNr
           << " at time " << timestamp_ms() << endl;
    }

    dT = screamTx->addTransmitted(timestamp_ms() * 1000, ssrc, size, seqNr);
  }

  /* isOkToTransmit() should be called again until dT seconds later */
  if (dT > 0.0f) {
    if (txTimer.is_disarmed())
      txTimer.arm((int) (dT * 1000));
  }

  /* No RTP packet available to transmit */
  if (dT == -1.0f)
    return;
}

/* Receive incoming RTCP feedback */
void recvRtcp(ScreamTx *screamTx, UDPSocket &socket)
{
  UDPSocket::received_datagram recd = socket.recv();
  /* Client timestamp (us) when received RTCP */
  uint64_t client_recv_rtcp_ts_us = recd.timestamp * 1000;

  /* Assemble RTCP packet */
  RtcpPacket rtcpPacket(recd.payload);

  if (debug) {
    cerr << "Received a RTCP packet acking sequence number "
         << rtcpPacket.header.ack_seq_num
         << " at time " << recd.timestamp << endl;
  }

  uint32_t ssrc = rtcpPacket.header.ssrc;
  /* Server timestamp (ms) when received the RTP packet that is acked by RTCP */
  uint32_t server_recv_rtp_ts_ms = rtcpPacket.header.recv_timestamp;
  uint16_t ack_seq_num = rtcpPacket.header.ack_seq_num;
  uint64_t ack_vector = rtcpPacket.header.ack_vector;

  /* Calculate one-way delay and RTT inside, then update CWND */
  screamTx->incomingFeedback(client_recv_rtcp_ts_us, ssrc,
                             server_recv_rtp_ts_ms, ack_seq_num,
                             ack_vector, false);
}

int main(int argc, char *argv[])
{
  if (argc == 4 && string(argv[3]) == "debug") {
    debug = true;
  } else if (argc != 3) {
    cerr << "Usage: " << argv[0] << " HOST PORT [debug]" << endl;
    return EXIT_FAILURE;
  }

  uint64_t start_time = timestamp_ms();
  cerr << "Client starts at " << start_time << endl;

  /* UDP socket for client */
  UDPSocket socket;
  socket.set_timestamps();
  socket.connect(Address(argv[1], argv[2]));

  float frameRate = 25.0f; /* encode 25 frames per second */
  ScreamTx *screamTx = new ScreamTx();
  RtpQueue *rtpQueue = new RtpQueue();
  /* Adopt the same parameters as in the original scream_01 experiment */
  VideoEnc *videoEnc = new VideoEnc(rtpQueue, frameRate, 0.1f, false, false, 0);
  screamTx->registerNewStream(
      rtpQueue, SSRC, 1.0f, 64e3f, 10e7f, 2e5f, 2.0f, 0.5f, 0.3f);

  /* Non-blocking timers for client and video encoder */
  Timerfd txTimer(TFD_NONBLOCK);
  Timerfd videoTimer(TFD_NONBLOCK);
  int encodeInterval_ms = (int) (1e3 / frameRate);
  videoTimer.arm(encodeInterval_ms, encodeInterval_ms);

  /* Always read the timer that returned POLLIN before arm it again */
  struct pollfd fds[3];
  fds[0].fd = txTimer.fd_num();
  fds[0].events = POLLIN;
  fds[1].fd = videoTimer.fd_num();
  fds[1].events = POLLIN;
  fds[2].fd = socket.fd_num();
  fds[2].events = POLLIN;

  while (timestamp_ms() - start_time <= tmax_ms) {
    SystemCall("poll", poll(fds, 3, -1));

    /* Tx timer expires */
    if (fds[0].revents & POLLIN) {
      if (txTimer.expirations() > 0)
        sendRtp(screamTx, rtpQueue, txTimer, socket);
    }

    /* Video timer expires */
    if (fds[1].revents & POLLIN) {
      if (videoTimer.expirations() > 0) {
        encodeVideoFrame(videoEnc, screamTx);
        if (txTimer.is_disarmed())
          sendRtp(screamTx, rtpQueue, txTimer, socket);
      }
    }

    /* Incoming RTCP feedback */
    if (fds[2].revents & POLLIN) {
      recvRtcp(screamTx, socket);
      if (txTimer.is_disarmed())
        sendRtp(screamTx, rtpQueue, txTimer, socket);
    }
  }

  delete screamTx;
  delete rtpQueue;
  delete videoEnc;

  return EXIT_SUCCESS;
}
