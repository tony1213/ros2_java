/* Copyright 2016 Esteve Fernandez <esteve@apache.org>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.ros2.rcljava.common;

public final class JNIUtils {
  /**
   * Private constructor so this cannot be instantiated.
   */
  private JNIUtils() { }

  public static void loadLibrary(Class cls, String typesupportIdentifier) {
    String className = cls.getCanonicalName();

    // Convert from camel case to underscores using the same regex as:
    // https://raw.githubusercontent.com/ros2/rosidl/master/rosidl_cmake/cmake/string_camel_case_to_lower_case_underscore.cmake
    String libraryName = className
        .replaceAll("\\.", "_")
        .replaceAll("(.)([A-Z][a-z]+)", "$1_$2")
        .replaceAll("([a-z0-9])([A-Z])", "$1_$2")
        .toLowerCase();

    libraryName = libraryName + "__" + typesupportIdentifier;

    System.loadLibrary(libraryName);
  }
}
