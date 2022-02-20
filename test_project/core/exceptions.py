

class UserNotFoundException(Exception):
    pass


class UserNotAdminException(Exception):
    pass


class UserExistsException(Exception):
    pass


class WrongPasswordException(Exception):
    pass


class ProjectNotFoundException(Exception):
    pass


class PermissionException(Exception):
    pass


class IssueNotFoundException(Exception):
    pass


class ProjectRequiredException(Exception):
    pass

