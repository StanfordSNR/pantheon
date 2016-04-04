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

    struct sockaddr_in remoteAddr;
    memset((char*)&remoteAddr, 0, sizeof(remoteAddr));
    remoteAddr.sin_family = AF_INET;
    remoteAddr.sin_port = htons(15000);
    remoteAddr.sin_addr.s_addr = inet_addr(argv[1]); 

    connect(localSocket, (struct sockaddr*)&remoteAddr, sizeof(remoteAddr));
    printf("Connected to server\n");
    printf("Input message to send\n");

    char send_buf[MAXDATASIZE];
    while (1) {
        if (fgets(send_buf, MAXDATASIZE, stdin)) {
            int sent_bytes = send(localSocket, send_buf, strlen(send_buf), 0);
            if (sent_bytes < 0)
                perror("send");
            else if (sent_bytes != strlen(send_buf))
                printf("partially sent\n");
        } else {
            send(localSocket, send_buf, 0, 0);
            break;
        }
    }

    close(localSocket);
    return 0;
}
