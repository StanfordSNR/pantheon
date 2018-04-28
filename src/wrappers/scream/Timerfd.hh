#ifndef TIMERFD_H
#define TIMERFD_H

#include <stdint.h>
#include <sys/timerfd.h>
#include "file_descriptor.hh"

class Timerfd : public FileDescriptor
{
public:
  /*
   * Default is blocking timer
   * Pass in TFD_NONBLOCK for non-blocking timer
   */
  Timerfd(int flags = 0);

  /* Start the timer with first expiration time and period */
  void arm(int first_exp_ms, int interval_ms = 0);

  /* Return true if the timer has stopped */
  bool is_disarmed();

  /* Return the number of expirations occurred */
  int expirations();
};

#endif /* TIMERFD_H */
