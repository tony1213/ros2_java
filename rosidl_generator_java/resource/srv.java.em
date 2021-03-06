package @(package_name).@(subfolder);

import org.ros2.rcljava.common.JNIUtils;
import org.ros2.rcljava.common.RCLJavaProxy;
import org.ros2.rcljava.interfaces.ServiceDefinition;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class @(type_name) implements ServiceDefinition {

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

  public static native long getServiceTypeSupport();

  public static final Class<@(type_name)_Request> RequestType = @(type_name)_Request.class;

  public static final Class<@(type_name)_Response> ResponseType = @(type_name)_Response.class;
}
