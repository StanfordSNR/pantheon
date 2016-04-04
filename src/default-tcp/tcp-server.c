#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
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

  char recv_buf[MAXDATASIZE + 1];
  while (1) {
    int recv_bytes = recv(remoteSocket, recv_buf, MAXDATASIZE, 0);
    if (recv_bytes > 0) {
      recv_buf[recv_bytes] = '\0';
      printf("%s", recv_buf);
    } else if (recv_bytes == 0) {
      printf("Client sent 0 bytes\n");
      break;
    }
  }

  close(localSocket);
  return 0;
}
