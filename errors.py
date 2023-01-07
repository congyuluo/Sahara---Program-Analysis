class CompilationError(Exception):
    pass


class ValgrindExecutionError(Exception):
    pass


class GProfExecutionError(Exception):
    pass


class MassifInterpreterError(Exception):
    pass


class GProfInterpreterError(Exception):
    pass