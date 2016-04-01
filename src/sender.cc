#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void print_usage() {
  // TODO
}

void exec_prog(char* prog_name, char* ip, char* port) {
  char* prog_argv[3]; 
  prog_argv[0] = prog_name;
  prog_argv[1] = ip;
  prog_argv[2] = port;

  if (execvp(prog_name, prog_argv) == -1) {
    perror(prog_name);
    exit(1);
  }
}

void parse(int argc, char* argv[]) {
  if (argc < 4) {
    print_usage();
    exit(1);
  }

  char* ip = argv[1];
  char* port = argv[2];
  
  if (strcasecmp(argv[3], "LEDBAT") == 0) {
    exec_prog("../external/libutp/ucat", ip, port); 
  }
}

int main(int argc, char* argv[]) {
  int pid;
  switch (pid = fork()) {
    case -1:
      perror("fork");
      break;
    case 0:
      parse(argc, argv);
      break;
    default:
      waitpid(pid, NULL, 0);
      break;
  }

  return 0;
}
