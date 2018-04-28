#ifndef PACKET_H
#define PACKET_H

#include <string>
#include <cstdint>

struct RtpPacket
{
  struct __attribute__((__packed__)) Header {
    uint32_t ssrc;
    uint16_t seq_num;
  } header;

  std::string payload;

  /* Create RTP packet with dummy payload */
  RtpPacket(uint32_t ssrc, uint32_t size, uint16_t seq_num);

  /* Parse incoming RTP packet */
  RtpPacket(std::string &str);

  /* Make wire representation of RTP packet */
  std::string to_string();
};

struct RtcpPacket
{
  struct __attribute__((__packed__)) Header {
    uint32_t ssrc;
    uint16_t ack_seq_num;
    uint64_t ack_vector;
    uint32_t recv_timestamp;
  } header;

  /* Create RTCP packet */
  RtcpPacket(uint32_t ssrc, uint16_t ack_seq_num,
             uint64_t ack_vector, uint32_t recv_timestamp);

  /* Parse incoming RTCP packet */
  RtcpPacket(std::string &str);

  /* Make wire representation of RTCP packet */
  std::string to_string();
};

#endif /* PACKET_H */
