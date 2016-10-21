#!/usr/bin/perl -w

use strict;

my $output_filename = 'pantheon_summary.pdf';

open GNUPLOT, qq{| gnuplot | inkscape -A $output_filename} .
              qq{ -z -b white /dev/stdin >/dev/null 2>&1} or die;

my $points;

sub prettify { # maybe this should be every driver's responsibility too!
  my ( $scheme ) = @_;
  $scheme =~ s{default_tcp}{TCP Cubic};
  $scheme =~ s{vegas}{TCP Vegas};
  $scheme =~ s{koho_cc}{KohoCC};
  $scheme =~ s{ledbat}{LEDBAT};
  $scheme =~ s{pcc}{PCC};
  $scheme =~ s{verus}{Verus};
  $scheme =~ s{scream}{SCReAM};
  $scheme =~ s{webrtc}{WebRTC media};
  $scheme =~ s{sprout}{Sprout};
  $scheme =~ s{quic}{QUIC Cubic (toy)};
  return $scheme;
}

my @data;
for my $scheme ( @ARGV ) {
  my $filename = $scheme . q{_stats.log};

  open ( my $file, q{<}, $filename ) or die qq{Cannot open $filename: $!};

  my %row;
  $row{ username } = prettify( $scheme );

  my $seen_data_link = 0;
  LINE: while ( <$file> ) {
    chomp;

    if ( m{Data link statistics} ) {
      $seen_data_link = 1;
    }

    if ( $seen_data_link ) {
      if ( m{^Average throughput: (.*?) Mbits} ) {
        die if exists $row{ throughput };
        $row{ throughput } = $1;
      } elsif ( m{^95th percentile signal delay: (.*?) ms} ) {
        die if exists $row{ delay };
        $row{ delay } = $1;
      }
    }

    if (defined $row{ throughput } and defined $row{ delay }) {
      last;
    }
  }

  close $file or die qq{Cannot close $filename: $!};

  die unless ( defined $row{ throughput } and defined $row{ delay } and defined $row{ username } );

  push @data, \%row;
}

my $delay_min = (sort { $a->{ delay } <=> $b->{ delay } } @data)[ 0 ]->{ delay };
my $delay_max = (sort { $a->{ delay } <=> $b->{ delay } } @data)[ -1 ]->{ delay };

$delay_min *= .8;
$delay_max *= 1.2;

my $tput_min = (sort { $a->{ throughput } <=> $b->{ throughput } } @data)[ 0 ]->{ throughput };
my $tput_max = (sort { $a->{ throughput } <=> $b->{ throughput } } @data)[ -1 ]->{ throughput };

print GNUPLOT <<END;
set xlabel "95th percentile of signal delay (ms)"
set ylabel "throughput (Mbit/s)"
set terminal svg size 1024,768 fixed fsize 20 rounded solid
set logscale x
unset key
set title "Summary of results"
set xrange [$delay_max:$delay_min] reverse
set yrange [*:*]
set xtics 2
END

sub relative_difference {
  my ( $a, $b, $min, $max ) = @_;
  my $diff = abs( $a - $b );
  my $overall_diff = abs( $max - $min );
  my $rdif = $diff / $overall_diff;
  return $rdif;
}

for my $elem1 ( @data ) {
  POSSIBLE_COLLISION: for my $elem2 ( @data ) {
    next POSSIBLE_COLLISION if $elem1 == $elem2;

    if ( relative_difference( $elem1->{ throughput }, $elem2->{ throughput },
                              $tput_max, $tput_min ) < 0.1 ) {
      if ( relative_difference( $elem1->{ delay }, $elem2->{ delay },
           $delay_min, $delay_max ) < 0.1 ) {
        my $orient = $elem1->{ delay } < $elem2->{ delay };
        $elem1->{ side } = $orient ? "left" : "right";
        $elem2->{ side } = $orient ? "right" : "left";
      }
    }
  }
}

for my $row ( @data ) {
  if ( not defined $row->{ side } ) {
    if ( log($row->{ delay }) > (log($delay_max) + log($delay_min)) / 2 ) {
      $row->{ side } = q{left};
    } else {
      $row->{ side } = q{right};
    }
  }

  my @offset = (0,0);

  if ( $row->{ side } eq q{right} ) {
    $offset[ 0 ] -= 1.25;
  }

  if ( $row->{ throughput } - $tput_min > 0.9 * ($tput_max - $tput_min) ) {
    $offset[ 1 ] -= .75;
  }

  $points .= qq{$row->{delay} $row->{throughput}\n};

  $row->{ username } =~ s{_}{-}g;
  print GNUPLOT qq{set label "$row->{ username }" at $row->{delay}, $row->{throughput} point $row->{ side } offset $offset[ 0 ], $offset[ 1 ]\n};
}

print GNUPLOT qq{plot "-" using 1:2 lt 7 ps 1.0 lc rgb "#d80000ff"\n};

print GNUPLOT $points;

close GNUPLOT or die qq{$!};
