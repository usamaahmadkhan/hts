# CMake generated Testfile for 
# Source directory: /root/hts/hts/tests/virtio
# Build directory: /root/hts/hts/build/tests/virtio
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(VirtioTest01_start_vm "/root/hts/hts/build/scripts/ctest_wrapper.sh" "600" "/root/hts/hts/tests/virtio" "VirtioTest01_start_vm" "python  test_kvm_virtio.py  --test_pattern=VirtioTest01 --conf conf.yaml --num_vcpus=4 --memory=8192")
set_tests_properties(VirtioTest01_start_vm PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
add_test(VirtioTest02_reboot_vm "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1000" "/root/hts/hts/tests/virtio" "VirtioTest02_reboot_vm" "python  test_kvm_virtio.py  --test_pattern=VirtioTest02 --conf conf.yaml --reboot_itr 4")
set_tests_properties(VirtioTest02_reboot_vm PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
add_test(VirtioTest03_run_iozone "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1800" "/root/hts/hts/tests/virtio" "VirtioTest03_run_iozone" "python  test_kvm_virtio.py  --test_pattern=VirtioTest03 --conf conf.yaml --num_vcpus=4 --memory=8192")
set_tests_properties(VirtioTest03_run_iozone PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
add_test(VirtioTest04_check_cpu_mem "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1800" "/root/hts/hts/tests/virtio" "VirtioTest04_check_cpu_mem" "python  test_kvm_virtio.py  --test_pattern=VirtioTest04 --conf conf.yaml --num_vcpus=4 --memory=8192 --max_vcpus=6 --max_mem=24000 --mem_tolerence=5")
set_tests_properties(VirtioTest04_check_cpu_mem PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
add_test(VirtioTest05_on_off_cpu "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1800" "/root/hts/hts/tests/virtio" "VirtioTest05_on_off_cpu" "python  test_kvm_virtio.py  --test_pattern=VirtioTest05 --conf conf.yaml --num_vcpus=4 --memory=8192")
set_tests_properties(VirtioTest05_on_off_cpu PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
add_test(VirtioTest06_reset_all_cpu "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1800" "/root/hts/hts/tests/virtio" "VirtioTest06_reset_all_cpu" "python  test_kvm_virtio.py  --test_pattern=VirtioTest06 --conf conf.yaml --num_vcpus=4 --memory=8192")
set_tests_properties(VirtioTest06_reset_all_cpu PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
add_test(VirtioTest07_run_dd_cmd "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1800" "/root/hts/hts/tests/virtio" "VirtioTest07_run_dd_cmd" "python  test_kvm_virtio.py  --test_pattern=VirtioTest07 --conf conf.yaml --num_vcpus=4 --memory=8192")
set_tests_properties(VirtioTest07_run_dd_cmd PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
add_test(VirtioTest08_run_ltp_tests "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1800" "/root/hts/hts/tests/virtio" "VirtioTest08_run_ltp_tests" "python  test_kvm_virtio.py  --test_pattern=VirtioTest08 --conf conf.yaml --num_vcpus=4 --memory=8192")
set_tests_properties(VirtioTest08_run_ltp_tests PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
add_test(VirtioTest09_run_gdb "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1800" "/root/hts/hts/tests/virtio" "VirtioTest09_run_gdb" "python  test_kvm_virtio.py  --test_pattern=VirtioTest09 --conf conf.yaml --num_vcpus=6 --memory=8192")
set_tests_properties(VirtioTest09_run_gdb PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
add_test(VirtioTest10_run_kbuild "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1800" "/root/hts/hts/tests/virtio" "VirtioTest10_run_kbuild" "python  test_kvm_virtio.py  --test_pattern=VirtioTest10 --conf conf.yaml --num_vcpus=6 --memory=8192")
set_tests_properties(VirtioTest10_run_kbuild PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
add_test(VirtioTest11_multiple_vm_creation "/root/hts/hts/build/scripts/ctest_wrapper.sh" "1800" "/root/hts/hts/tests/virtio" "VirtioTest11_multiple_vm_creation" "python  test_kvm_virtio.py  --test_pattern=VirtioTest11 --conf conf.yaml --num_vcpus=2 --memory=2048 --num_vm=3")
set_tests_properties(VirtioTest11_multiple_vm_creation PROPERTIES  LABELS "type:unit" TIMEOUT "13000" WORKING_DIRECTORY "/root/hts/hts/tests/virtio")
