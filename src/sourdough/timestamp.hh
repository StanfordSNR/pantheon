#ifndef TIMESTAMP_HH
#define TIMESTAMP_HH

#include <ctime>
#include <cstdint>

/* Current time in milliseconds since the start of the program */
uint64_t timestamp_ms( void );
uint64_t timestamp_ms( const timespec & ts );

/* Return time in macroseconds */
uint64_t timestamp_us( void );

#endif /* TIMESTAMP_HH */
