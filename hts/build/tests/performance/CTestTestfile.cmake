# CMake generated Testfile for 
# Source directory: /root/hts/hts/tests/performance
# Build directory: /root/hts/hts/build/tests/performance
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(PerfTest01_fio_read "/root/hts/hts/build/scripts/ctest_wrapper.sh" "11000" "/root/hts/hts/tests/performance" "PerfTest01_fio_read" "python  test_kvm_perf.py  --test_pattern=PerfTest01 --conf conf.yaml --num_vcpus=4 --memory=8192 --io_pattern=read --runtime=100")
set_tests_properties(PerfTest01_fio_read PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/performance")
add_test(PerfTest02_fio_write "/root/hts/hts/build/scripts/ctest_wrapper.sh" "11000" "/root/hts/hts/tests/performance" "PerfTest02_fio_write" "python  test_kvm_perf.py  --test_pattern=PerfTest01 --conf conf.yaml --num_vcpus=4 --memory=8192 --io_pattern=write --runtime=100")
set_tests_properties(PerfTest02_fio_write PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/performance")
add_test(PerfTest03_fio_randread "/root/hts/hts/build/scripts/ctest_wrapper.sh" "11000" "/root/hts/hts/tests/performance" "PerfTest03_fio_randread" "python  test_kvm_perf.py  --test_pattern=PerfTest01 --conf conf.yaml --num_vcpus=4 --memory=8192 --io_pattern=randread --runtime=100")
set_tests_properties(PerfTest03_fio_randread PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/performance")
add_test(PerfTest04_fio_randwrite "/root/hts/hts/build/scripts/ctest_wrapper.sh" "11000" "/root/hts/hts/tests/performance" "PerfTest04_fio_randwrite" "python  test_kvm_perf.py  --test_pattern=PerfTest01 --conf conf.yaml --num_vcpus=4 --memory=8192 --io_pattern=randwrite --runtime=100")
set_tests_properties(PerfTest04_fio_randwrite PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/performance")
add_test(PerfTest05_network_latency "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1800" "/root/hts/hts/tests/performance" "PerfTest05_network_latency" "python  test_kvm_perf.py  --test_pattern=PerfTest02 --conf conf.yaml --num_vcpus=4 --memory=8192 --num_vm=2")
set_tests_properties(PerfTest05_network_latency PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/performance")
