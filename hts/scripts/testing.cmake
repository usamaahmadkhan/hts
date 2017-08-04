function(virtio_add_test)
  PARSE_ARGUMENTS(TEST "NAME;CONFIGURATIONS;WORKING_DIRECTORY;COMMAND;TIMEOUT" "UNSTABLE" ${ARGN})
  if(NOT TEST_NAME)
    list(GET TEST_DEFAULT_ARGS 0 TEST_NAME)
    list(REMOVE_AT TEST_DEFAULT_ARGS 0)
  endif()
  if(NOT TEST_WORKING_DIRECTORY)
    set(TEST_WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
  endif()
  if(NOT TEST_COMMAND)
    set(TEST_COMMAND ${TEST_DEFAULT_ARGS})
  endif()
  if(NOT TEST_TIMEOUT)
    set(TEST_TIMEOUT "13000")
  endif()
  set(TEST_LABELS "")
  set(TEST_DISABLED False)

  # Check if test is unstable
  if(TEST_UNSTABLE)
    set(TEST_NAME "UNSTABLE_${TEST_NAME}")
    if ("$ENV{EXCLUDE_UNSTABLE}" EQUAL "1")
      set(TEST_DISABLED True)
    endif()
  endif()

  if(NOT TEST_DISABLED)
    add_test(NAME ${TEST_NAME}
      CONFIGURATIONS ${CONFIGURATIONS}
      WORKING_DIRECTORY ${TEST_WORKING_DIRECTORY}
      COMMAND ${CMAKE_BINARY_DIR}/scripts/ctest_wrapper.sh ${TEST_TIMEOUT} ${TEST_WORKING_DIRECTORY} ${TEST_NAME} ${TEST_COMMAND})
    # This timeout is a safety net, just in case the timeout handling internal to the test fails.
    set_tests_properties(${TEST_NAME} PROPERTIES TIMEOUT 13000)
    if(TEST_TIMEOUT GREATER 13000)
      message(FATAL_ERROR
        "${TEST_NAME} tried to declare a timeout of ${TEST_TIMEOUT}, that is greater than the limit of 2000")
    endif()


    # Add some tags to the test, in format "tagname:tagvalue", that
    # can be used by Jenkins when reading CTest's XML output (ctest -T
    # Test).
    #
    # Supported tags:
    # - type: type of test (local)
    # - runtime: runtime properties of the test (none=core=pre-checkin, nightly)
    # - priority: severity of the test (none=critical, unstable)

    list(APPEND TEST_LABELS "type:unit")
    if(TEST_UNSTABLE)
      list(APPEND TEST_LABELS "priority:unstable")
    endif()
    set_tests_properties(${TEST_NAME} PROPERTIES LABELS "${TEST_LABELS}")
  endif()
endfunction()
