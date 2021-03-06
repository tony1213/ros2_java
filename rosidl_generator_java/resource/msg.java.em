package @(package_name).@(subfolder);

import org.ros2.rcljava.common.JNIUtils;
import org.ros2.rcljava.common.RCLJavaProxy;
import org.ros2.rcljava.interfaces.MessageDefinition;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@[for field in spec.fields]@
@[    if not field.type.is_primitive_type()]@
import @(field.type.pkg_name).msg.@(field.type.type);
@[    end if]@
@[end for]@

public final class @(type_name) implements MessageDefinition {

  private static final Logger logger = LoggerFactory.getLogger(@(type_name).class);

  static {
    java.lang.String typesupportIdentifier = RCLJavaProxy.getTypesupportIdentifier();
    if (typesupportIdentifier == null) {
      logger.debug("Typesupport identifier can't be found");
    } else {
      try {
        JNIUtils.loadLibrary(@(type_name).class, typesupportIdentifier);
      } catch (UnsatisfiedLinkError ule) {
        logger.error("Native code library failed to load.\n" + ule);
        System.exit(1);
      }
    }
  }

  public static native long getFromJavaConverter();
  public static native long getToJavaConverter();
  public static native long getTypeSupport();

  public long getFromJavaConverterInstance() {
    return getFromJavaConverter();
  }

  public long getToJavaConverterInstance() {
    return getToJavaConverter();
  }

  public long getTypeSupportInstance() {
    return getTypeSupport();
  }

@[for constant in spec.constants]@
    public static final @(get_builtin_java_type(constant.type)) @(constant.name) = @(constant_value_to_java(constant.type, constant.value));
@[end for]@

@[for field in spec.fields]@

@[    if field.type.is_array]@
@[        if field.default_value is not None]@
  private java.util.List<@(get_java_type(field.type, use_primitives=False))> @(field.name) = java.util.Arrays.asList(new @(get_java_type(field.type, use_primitives=False))[] @(value_to_java(field.type, field.default_value)));
@[        else]@
  private java.util.List<@(get_java_type(field.type, use_primitives=False))> @(field.name);
@[        end if]@

  public final void set@(convert_lower_case_underscore_to_camel_case(field.name))(final java.util.Collection<@(get_java_type(field.type, use_primitives=False))> @(field.name)) {
@[        if field.type.array_size]@
@[            if field.type.is_upper_bound]@
    if(@(field.name).size() > @(field.type.array_size)) {
        throw new IllegalArgumentException("List too big, maximum size allowed: @(field.type.array_size)");
@[            else]@
    if(@(field.name).size() != @(field.type.array_size)) {
        throw new IllegalArgumentException("Invalid size for fixed array, must be exactly: @(field.type.array_size)");
@[            end if]@
    }
@[        end if]@
    if (@(field.name) != null) {
      this.@(field.name) = new java.util.ArrayList<@(get_java_type(field.type, use_primitives=False))>(@(field.name));
    }
  }

  public final java.util.List<@(get_java_type(field.type, use_primitives=False))> get@(convert_lower_case_underscore_to_camel_case(field.name))() {
    if (this.@(field.name) == null) {
      return null;
    }
    return new java.util.ArrayList<@(get_java_type(field.type, use_primitives=False))>(this.@(field.name));
  }
@[    else]@
@[        if field.default_value is not None]@
  private @(get_java_type(field.type)) @(field.name) = @(value_to_java(field.type, field.default_value));
@[        else]@
@[            if field.type.type == 'string']@
  private @(get_java_type(field.type)) @(field.name) = "";
@[            else]@
  private @(get_java_type(field.type)) @(field.name);
@[            end if]@
@[        end if]@

  public void set@(convert_lower_case_underscore_to_camel_case(field.name))(final @(get_java_type(field.type)) @(field.name)) {
@[        if field.type.string_upper_bound]@
    if(@(field.name).length() > @(field.type.string_upper_bound)) {
        throw new IllegalArgumentException("String too long, maximum size allowed: @(field.type.string_upper_bound)");
    }
@[        end if]@

    this.@(field.name) = @(field.name);
  }

  public @(get_java_type(field.type)) get@(convert_lower_case_underscore_to_camel_case(field.name))() {
    return this.@(field.name);
  }
@[    end if]@
@[end for]@
}
