#define LOGURU_IMPLEMENTATION 1
#include <loguru/loguru.hpp>

int main(int argc, char* argv[]) {
  loguru::init(argc, argv);
  LOG_S(INFO) << "Hello from loguru";
  return 0;
}
