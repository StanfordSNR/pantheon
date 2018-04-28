AM_CPPFLAGS = $(CXX11_FLAGS) -I../../third_party/sourdough/src \
                             -I../../third_party/scream/code
AM_CXXFLAGS = $(PICKY_CXXFLAGS)

LDADD = ../../third_party/sourdough/src/libsourdough.a -lpthread

bin_PROGRAMS = ScreamClient ScreamServer

ScreamClient_SOURCES = \
    ScreamClient.cc Packet.hh Packet.cc Timerfd.hh Timerfd.cc \
    ../../third_party/scream/code/ScreamTx.h \
    ../../third_party/scream/code/ScreamTx.cpp \
    ../../third_party/scream/code/RtpQueue.h \
    ../../third_party/scream/code/RtpQueue.cpp \
    ../../third_party/scream/code/VideoEnc.h \
    ../../third_party/scream/code/VideoEnc.cpp

ScreamServer_SOURCES = \
    ScreamServer.cc Packet.hh Packet.cc Timerfd.hh Timerfd.cc \
    ../../third_party/scream/code/ScreamRx.h \
    ../../third_party/scream/code/ScreamRx.cpp
