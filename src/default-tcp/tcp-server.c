#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/poll.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <string.h>
#include <unistd.h>

#define MAXDATASIZE 1515

int main(int argc, char** argv) {
  int localSocket = socket(AF_INET, SOCK_STREAM, 0);

  struct sockaddr_in localAddr;
  memset((char*)&localAddr, 0, sizeof(localAddr));
  localAddr.sin_family = AF_INET;
  localAddr.sin_port = htons(15000);
  localAddr.sin_addr.s_addr = htonl(INADDR_ANY);

  if (bind(localSocket, (struct sockaddr*)&localAddr, sizeof(localAddr)) < 0) {
    printf("bind failed\n");
    return 0;
  }
  printf("Server address: %s\n", inet_ntoa(localAddr.sin_addr));

  listen(localSocket, 10);

  struct sockaddr_in remoteAddr;
  socklen_t remoteAddrLen;
  int remoteSocket = accept(localSocket, 
      (struct sockaddr*)&remoteAddr, &remoteAddrLen);
  printf("Connected to client\n");

  char send_buf[MAXDATASIZE];
  char recv_buf[MAXDATASIZE];

  struct pollfd ufds[2];
  ufds[0].fd = STDIN_FILENO;
  ufds[0].events = POLLIN; 

  ufds[1].fd = remoteSocket;
  ufds[1].events = POLLIN; 

  int rv;
  while (1) {
    rv = poll(ufds, 2, 10000);
    if (rv == -1) {
      perror("poll");
    } else if (rv == 0) {
      printf("No data after 10 seconds timeout");
    } else {
      if (ufds[0].revents & POLLIN) {
        if (fgets(send_buf, MAXDATASIZE - 1, stdin)) {
          int sent_bytes = send(remoteSocket, send_buf, strlen(send_buf), 0);
          if (sent_bytes < 0)
            perror("send");
          else if (sent_bytes != strlen(send_buf))
            printf("Partially sent\n");
        } else {
          send(localSocket, send_buf, 0, 0);
          break;
        }
      }

      if (ufds[1].revents & POLLIN) {
        int recv_bytes = recv(remoteSocket, recv_buf, MAXDATASIZE - 1, 0);
        if (recv_bytes > 0) {
          recv_buf[recv_bytes] = '\0';
          printf("%s", recv_buf);
        } else if (recv_bytes == 0) {
          printf("The other side has closed connection\n");
          break;
        }
      }
    }
  }

  close(localSocket);
  return 0;
}
