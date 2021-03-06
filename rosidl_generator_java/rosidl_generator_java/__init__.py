# Copyright 2016 Esteve Fernandez <esteve@apache.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import defaultdict
import os

from rosidl_cmake import convert_camel_case_to_lower_case_underscore
from rosidl_cmake import expand_template
from rosidl_cmake import get_newest_modification_time
from rosidl_cmake import read_generator_arguments
from rosidl_parser import parse_message_file
from rosidl_parser import parse_service_file


# Taken from http://stackoverflow.com/a/6425628
def convert_lower_case_underscore_to_camel_case(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


def generate_java(generator_arguments_file, typesupport_impl, typesupport_impls):
    args = read_generator_arguments(generator_arguments_file)
    typesupport_impls = typesupport_impls.split(';')

    template_dir = args['template_dir']
    type_support_impl_by_filename = {
        '%s.ep.{0}.cpp'.format(impl): impl for impl in typesupport_impls
    }
    mapping_msgs = {
        os.path.join(template_dir, 'msg.java.em'): ['%s.java'],
        os.path.join(template_dir, 'msg.cpp.em'):
        type_support_impl_by_filename.keys(),
    }

    mapping_srvs = {
        os.path.join(template_dir, 'srv.java.em'): ['%s.java'],
        os.path.join(template_dir, 'srv.cpp.em'):
        type_support_impl_by_filename.keys(),
    }

    for template_file in mapping_msgs.keys():
        assert os.path.exists(template_file), \
            'Messages template file %s not found' % template_file
    for template_file in mapping_srvs.keys():
        assert os.path.exists(template_file), \
            'Services template file %s not found' % template_file

    functions = {
        'get_java_type': get_java_type,
    }
    latest_target_timestamp = get_newest_modification_time(args['target_dependencies'])

    modules = defaultdict(list)
    for ros_interface_file in args['ros_interface_files']:
        extension = os.path.splitext(ros_interface_file)[1]
        subfolder = os.path.basename(os.path.dirname(ros_interface_file))
        if extension == '.msg':
            spec = parse_message_file(args['package_name'], ros_interface_file)
            mapping = mapping_msgs
            type_name = spec.base_type.type
        elif extension == '.srv':
            spec = parse_service_file(args['package_name'], ros_interface_file)
            mapping = mapping_srvs
            type_name = spec.srv_name
        else:
            continue

        module_name = convert_camel_case_to_lower_case_underscore(type_name)
        modules[subfolder].append((module_name, type_name))
        package_name = args['package_name']
        jni_package_name = package_name.replace('_', '_1')
        jni_type_name = type_name.replace('_', '_1')
        for template_file, generated_filenames in mapping.items():
            for generated_filename in generated_filenames:
                data = {
                    'constant_value_to_java': constant_value_to_java,
                    'value_to_java': value_to_java,
                    'convert_camel_case_to_lower_case_underscore':
                    convert_camel_case_to_lower_case_underscore,
                    'convert_lower_case_underscore_to_camel_case':
                    convert_lower_case_underscore_to_camel_case,
                    'get_builtin_java_type': get_builtin_java_type,
                    'module_name': module_name, 'package_name': package_name,
                    'jni_package_name': jni_package_name,
                    'jni_type_name': jni_type_name,
                    'spec': spec, 'subfolder': subfolder,
                    'typesupport_impl': type_support_impl_by_filename.get(generated_filename, ''),
                    'typesupport_impls': typesupport_impls,
                    'type_name': type_name,
                }
                data.update(functions)
                generated_file = os.path.join(
                    args['output_dir'], subfolder, generated_filename % type_name)
                expand_template(
                    template_file, data, generated_file,
                    minimum_timestamp=latest_target_timestamp)

    return 0


def escape_string(s):
    s = s.replace('\\', '\\\\')
    s = s.replace("'", "\\'")
    return s


def value_to_java(type_, value):
    assert type_.is_primitive_type()
    assert value is not None

    if not type_.is_array:
        return primitive_value_to_java(type_, value)

    java_values = []
    for single_value in value:
        java_value = primitive_value_to_java(type_, single_value)
        java_values.append(java_value)
    return '{%s}' % ', '.join(java_values)


def primitive_value_to_java(type_, value):
    assert type_.is_primitive_type()
    assert value is not None

    if type_.type == 'bool':
        return 'true' if value else 'false'

    if type_.type in [
        'byte',
        'char',
        'int8', 'uint8',
        'int16', 'uint16',
        'int32', 'uint32',
        'int64', 'uint64',
        'float64',
    ]:
        return str(value)

    if type_.type == 'float32':
        return '%sf' % value

    if type_.type == 'string':
        return '"%s"' % escape_string(value)

    assert False, "unknown primitive type '%s'" % type_


def constant_value_to_java(type_, value):
    assert value is not None

    if type_ == 'bool':
        return 'true' if value else 'false'

    if type_ in [
        'byte',
        'char',
        'int8', 'uint8',
        'int16', 'uint16',
        'int32', 'uint32',
        'int64', 'uint64',
        'float64',
    ]:
        return str(value)

    if type_ == 'float32':
        return '%sf' % value

    if type_ == 'string':
        return '"%s"' % escape_string(value)

    assert False, "unknown constant type '%s'" % type_


def get_builtin_java_type(type_, use_primitives=True):
    if type_ == 'bool':
        return 'boolean' if use_primitives else 'java.lang.Boolean'

    if type_ == 'byte':
        return 'byte' if use_primitives else 'java.lang.Byte'

    if type_ == 'char':
        return 'char' if use_primitives else 'java.lang.Character'

    if type_ == 'float32':
        return 'float' if use_primitives else 'java.lang.Float'

    if type_ == 'float64':
        return 'double' if use_primitives else 'java.lang.Double'

    if type_ in ['int8', 'uint8']:
        return 'byte' if use_primitives else 'java.lang.Byte'

    if type_ in ['int16', 'uint16']:
        return 'short' if use_primitives else 'java.lang.Short'

    if type_ in ['int32', 'uint32']:
        return 'int' if use_primitives else 'java.lang.Integer'

    if type_ in ['int64', 'uint64']:
        return 'long' if use_primitives else 'java.lang.Long'

    if type_ == 'string':
        return 'java.lang.String'

    assert False, "unknown type '%s'" % type_


def get_java_type(type_, use_primitives=True, subfolder='msg'):
    if not type_.is_primitive_type():
        return '%s.%s.%s' % (type_.pkg_name, subfolder, type_.type)

    return get_builtin_java_type(type_.type, use_primitives=use_primitives)
