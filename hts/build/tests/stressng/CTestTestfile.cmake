# CMake generated Testfile for 
# Source directory: /root/hts/hts/tests/stressng
# Build directory: /root/hts/hts/build/tests/stressng
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(StressngTest01 "/root/hts/hts/build/scripts/ctest_wrapper.sh" "600" "/root/hts/hts/tests/stressng" "StressngTest01" "python  test_kvm_stressng.py  --test_pattern=StressngTest01 --conf conf.yaml --num_vcpus=4 --memory=8192")
set_tests_properties(StressngTest01 PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/stressng")
add_test(StressngTest02 "/root/hts/hts/build/scripts/ctest_wrapper.sh" "600" "/root/hts/hts/tests/stressng" "StressngTest02" "python  test_kvm_stressng.py  --test_pattern=StressngTest02 --conf conf.yaml --num_vcpus=4 --memory=8192")
set_tests_properties(StressngTest02 PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/stressng")
