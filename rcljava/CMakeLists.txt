cmake_minimum_required(VERSION 3.5)

project(rcljava)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_export_jars REQUIRED)
find_package(rcl REQUIRED)
find_package(rmw REQUIRED)
find_package(rmw_implementation_cmake REQUIRED)
find_package(rcljava_common REQUIRED)

include(CrossCompilingExtra)

if(ANDROID)
  find_host_package(Java COMPONENTS Development)
else()
  find_package(Java COMPONENTS Development)
  find_package(JNI REQUIRED)
endif()

include(UseJava)
include(JavaExtra)

set(CMAKE_JAVA_COMPILE_FLAGS "-source" "1.6" "-target" "1.6")

if(NOT WIN32)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Wextra")
endif()

include_directories(include)

macro(target)
  if(NOT "${target_suffix} " STREQUAL " ")
    get_rcl_information("${rmw_implementation}" "rcl${target_suffix}")
  endif()

  set(${PROJECT_NAME}_jni_sources
    "src/main/cpp/org_ros2_rcljava_RCLJava.cpp"
    "src/main/cpp/org_ros2_rcljava_client_ClientImpl.cpp"
    "src/main/cpp/org_ros2_rcljava_node_NodeImpl.cpp"
    "src/main/cpp/org_ros2_rcljava_publisher_PublisherImpl.cpp"
    "src/main/cpp/org_ros2_rcljava_service_ServiceImpl.cpp"
    "src/main/cpp/org_ros2_rcljava_subscription_SubscriptionImpl.cpp"
  )

  foreach(_jni_source ${${PROJECT_NAME}_jni_sources})

    get_filename_component(_target_name "${_jni_source}" NAME_WE)
    set(_target_name "${_target_name}${target_suffix}")
    string_camel_case_to_lower_case_underscore("${_target_name}" _target_name)

    add_library(
      ${_target_name}
      SHARED ${_jni_source}
    )
    target_compile_definitions(${_target_name}
      PRIVATE "RMW_IMPLEMENTATION_SUFFIX=${target_suffix}")

    if(WIN32)
      set(_build_types ";_DEBUG;_MINSIZEREL;_RELEASE;_RELWITHDEBINFO")
    else()
      set(_build_types "")
    endif()

    foreach(_build_type ${_build_types})
      set_target_properties(${_target_name} PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY${_build_type} "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}"
        RUNTIME_OUTPUT_DIRECTORY${_build_type} "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}"
      )
    endforeach()

    ament_target_dependencies(${_target_name}
      "rcl${target_suffix}"
      "rcljava_common"
    )

    target_include_directories(${_target_name}
      PUBLIC
      ${JNI_INCLUDE_DIRS}
    )

    ament_export_libraries(${_target_name})

    install(TARGETS ${_target_name}
      ARCHIVE DESTINATION lib
      LIBRARY DESTINATION lib
    )

  endforeach()

endmacro()

set(${PROJECT_NAME}_sources
  "src/main/java/org/ros2/rcljava/RCLJava.java"
  "src/main/java/org/ros2/rcljava/client/ClientImpl.java"
  "src/main/java/org/ros2/rcljava/client/Client.java"
  "src/main/java/org/ros2/rcljava/concurrent/RCLFuture.java"
  "src/main/java/org/ros2/rcljava/consumers/BiConsumer.java"
  "src/main/java/org/ros2/rcljava/consumers/Consumer.java"
  "src/main/java/org/ros2/rcljava/consumers/TriConsumer.java"
  "src/main/java/org/ros2/rcljava/node/NodeImpl.java"
  "src/main/java/org/ros2/rcljava/node/Node.java"
  "src/main/java/org/ros2/rcljava/publisher/PublisherImpl.java"
  "src/main/java/org/ros2/rcljava/publisher/Publisher.java"
  "src/main/java/org/ros2/rcljava/qos/policies/Durability.java"
  "src/main/java/org/ros2/rcljava/qos/policies/History.java"
  "src/main/java/org/ros2/rcljava/qos/policies/QoSPolicy.java"
  "src/main/java/org/ros2/rcljava/qos/policies/Reliability.java"
  "src/main/java/org/ros2/rcljava/qos/QoSProfile.java"
  "src/main/java/org/ros2/rcljava/service/RMWRequestId.java"
  "src/main/java/org/ros2/rcljava/service/ServiceImpl.java"
  "src/main/java/org/ros2/rcljava/service/Service.java"
  "src/main/java/org/ros2/rcljava/subscription/SubscriptionImpl.java"
  "src/main/java/org/ros2/rcljava/subscription/Subscription.java"
)

add_jar("${PROJECT_NAME}_jar"
  "${${PROJECT_NAME}_sources}"
  OUTPUT_NAME
  "${PROJECT_NAME}"
  INCLUDE_JARS
  "${rcljava_common_JARS}"
)

call_for_each_rmw_implementation(target)

install_jar("${PROJECT_NAME}_jar" "share/${PROJECT_NAME}/java")
ament_export_jars("share/${PROJECT_NAME}/java/${PROJECT_NAME}.jar")

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  set(${PROJECT_NAME}_message_files
    "msg/BoundedArrayNested.msg"
    "msg/BoundedArrayPrimitives.msg"
    "msg/Builtins.msg"
    "msg/DynamicArrayNested.msg"
    "msg/DynamicArrayPrimitives.msg"
    "msg/Empty.msg"
    "msg/FieldsWithSameType.msg"
    "msg/Nested.msg"
    "msg/Primitives.msg"
    "msg/StaticArrayNested.msg"
    "msg/StaticArrayPrimitives.msg"
    "msg/UInt32.msg"
  )

  set(${PROJECT_NAME}_service_files
    "srv/AddTwoInts.srv"
  )

  rosidl_generate_interfaces(${PROJECT_NAME}
    ${${PROJECT_NAME}_message_files}
    ${${PROJECT_NAME}_service_files}
    DEPENDENCIES builtin_interfaces
    SKIP_INSTALL
  )

  get_property(_${PROJECT_NAME}_jar_file
    TARGET "${PROJECT_NAME}_jar"
    PROPERTY "JAR_FILE")

  get_property(_${PROJECT_NAME}_messages_jar_file
    TARGET "${PROJECT_NAME}_messages_jar"
    PROPERTY "JAR_FILE")

  set(${PROJECT_NAME}_test_sources
    "src/test/java/org/ros2/rcljava/RCLJavaTest.java"
    "src/test/java/org/ros2/rcljava/client/ClientTest.java"
    "src/test/java/org/ros2/rcljava/node/NodeTest.java"
    "src/test/java/org/ros2/rcljava/publisher/PublisherTest.java"
    "src/test/java/org/ros2/rcljava/subscription/SubscriptionTest.java"
  )

  set(${PROJECT_NAME}_testsuites
    "org.ros2.rcljava.RCLJavaTest"
    "org.ros2.rcljava.client.ClientTest"
    "org.ros2.rcljava.node.NodeTest"
    "org.ros2.rcljava.publisher.PublisherTest"
    "org.ros2.rcljava.subscription.SubscriptionTest"
  )

  set(_deps_library_paths "")
  foreach(_dep_lib ${rcljava_test_msgs_LIBRARIES})
    get_filename_component(_dep_dir "${_dep_lib}" DIRECTORY)
    list(APPEND _deps_library_paths ${_dep_dir})
  endforeach()
  foreach(_dep_lib ${std_msgs_LIBRARIES})
    get_filename_component(_dep_dir "${_dep_lib}" DIRECTORY)
    list(APPEND _deps_library_paths ${_dep_dir})
  endforeach()
  foreach(_dep_lib ${builtin_interfaces_LIBRARIES})
    get_filename_component(_dep_dir "${_dep_lib}" DIRECTORY)
    list(APPEND _deps_library_paths ${_dep_dir})
  endforeach()
  list(APPEND _deps_library_paths ${CMAKE_CURRENT_BINARY_DIR})
  list(APPEND _deps_library_paths ${CMAKE_CURRENT_BINARY_DIR}/rosidl_generator_java/rcljava/msg/)
  list(APPEND _deps_library_paths ${CMAKE_CURRENT_BINARY_DIR}/rosidl_generator_java/rcljava/srv/)

  foreach(testsuite ${${PROJECT_NAME}_testsuites})
    add_junit_tests("${PROJECT_NAME}_tests_${testsuite}"
      "${${PROJECT_NAME}_test_sources}"
      TESTS
      "${testsuite}"
      INCLUDE_JARS
      "${rcljava_common_JARS}"
      "${rcljava_test_msgs_JARS}"
      "${std_msgs_JARS}"
      "${builtin_interfaces_JARS}"
      "${_${PROJECT_NAME}_jar_file}"
      "${_${PROJECT_NAME}_messages_jar_file}"
      LIBRARY_PATHS
      "${_deps_library_paths}"
    )

    add_dependencies("${PROJECT_NAME}_tests_${testsuite}" "${PROJECT_NAME}_messages_jar")
  endforeach()

endif()

ament_package()
