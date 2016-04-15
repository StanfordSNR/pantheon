#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>

int generate_random_port() {
  return rand() % 10000 + 10000;
}

int main(int argc, char **argv) {
  srand(time(NULL));

  int local_socket = socket(AF_INET, SOCK_STREAM, 0);
  if (local_socket < 0) {
    perror("socket");
    exit(1);
  }

  int yes = 1;
  if (setsockopt(local_socket, SOL_SOCKET, SO_REUSEADDR, &yes,
    sizeof(int)) < 0) {
    perror("setsockopt");
    exit(1);
  }

  struct sockaddr_in local_addr;
  memset((char *) &local_addr, 0, sizeof(local_addr));
  local_addr.sin_family = AF_INET;
  local_addr.sin_addr.s_addr = htonl(INADDR_ANY);

  int port;
  while (1) {
    port = generate_random_port();
    local_addr.sin_port = htons(port);
    if (bind(local_socket, (struct sockaddr *) &local_addr,
      sizeof(local_addr)) < 0) {
      perror("bind");
    } else {
      break;
    }
  }

  printf("%d", port);
  return 0;
}
