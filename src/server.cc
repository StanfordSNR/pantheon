#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

void print_usage() {
  // TODO
}

void exec_prog(char* prog_name, char* prog_argv[]) {
  if (execvp(prog_name, prog_argv) == -1) {
    perror(prog_name);
    exit(1);
  }
}

void parse(int argc, char* argv[]) {
  if (argc < 2) {
    print_usage();
    exit(1);
  }

  if (strcasecmp(argv[1], "TCP") == 0) {
    exec_prog("default-tcp/tcp-server", NULL);
    return;
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
