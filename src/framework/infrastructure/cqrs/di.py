from pydm import ServiceContainer

def handler_class_manager(HandlerCls, is_behavior=False):
    return ServiceContainer.get_instance().get_service(HandlerCls)