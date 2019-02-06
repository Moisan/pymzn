
from ..dzn import dict2dzn, dzn2dict
from ..exceptions import *

from queue import Queue


class Solutions:
    """Represents a solution stream from the `minizinc` function.

    This class populates lazily but can be referenced and iterated as a list.

    Attributes
    ----------
    complete : bool
        Whether the stream includes the complete set of solutions. This means
        the stream contains all solutions in a satisfiability problem, or it
        contains the global optimum for maximization/minimization problems.
    """
    def __init__(self, queue *, keep=True):
        self._queue = queue
        self._keep = keep
        self._solns = [] if keep else None
        self._n_solns = 0
        self.complete = False
        self.stats = None

    @property
    def statistics(self):
        return self.stats

    def _fetch(self):
        while not self.queue.empty():
            soln = self.queue.get_nowait()
            if self._keep:
                self._solns.append(soln)
            self._n_solns += 1
            yield soln

    def _fetch_all(self):
        for soln in self._fetch():
            pass

    def __len__(self):
        return self._n_solns

    def __iter__(self):
        if self._keep:
            self._fetch_all()
            return iter(self._solns)
        else:
            return self._fetch()

    def __getitem__(self, key):
        if not self._keep:
            raise RuntimeError(
                'Cannot address directly if keep_solutions is False'
            )
        self._fetch_all()
        return self._solns[key]

    def __repr__(self):
        if self._keep:
            self._fetch_all()
            return repr(self._solns)
        else:
            return repr(self)

    def __str__(self):
        if self._keep:
            self._fetch_all()
            return str(self._solns)
        else:
            return str(self)


class SolutionParser:

    SOLN_SEP = '----------'
    SEARCH_COMPLETE = '=========='
    UNSATISFIABLE = '=====UNSATISFIABLE====='
    UNKNOWN = '=====UNKNOWN====='
    UNBOUNDED = '=====UNBOUNDED====='
    UNSATorUNBOUNDED = '=====UNSATorUNBOUNDED====='
    ERROR = '=====ERROR====='

    def __init__(self, mzn_file, solver, output_mode='dict'):
        self.mzn_file = mzn_file
        self.solver = solver
        self.output_mode = output_mode
        self._solns = None
        self.complete = False
        self.stats = None

    def _gather(self, solns, proc):
        try:
            for soln in self._parse(proc.stdout_data.splitlines()):
                solns.queue.put(soln)
            solns.complete = self.complete
            solns.stats = self.stats
        except MiniZincError as err:
            err._set(self.mzn_file, proc.stderr_data)
            raise err

    def parse(self, proc):
        queue = Queue()
        solns = Solutions(queue)
        self._gather(solns, proc)
        return solns

    def _parse(self, out):
        out = self.solver.parse_out(out)
        solns = self._split_solns(out)
        if self.output_mode == 'dict':
            solns = self._to_dict(solns)
        return solns

    def _split_solns(self, lines):
        """Split the solutions from the output stream of a solver or solns2out"""
        _buffer = []
        complete = False
        for line in lines:
            line = line.strip()
            if line == self.SOLN_SEP:
                yield '\n'.join(_buffer)
                _buffer = []
            elif line == self.SEARCH_COMPLETE:
                self.complete = True
                _buffer = []
            elif line == self.UNKNOWN:
                raise MiniZincUnknownError
            elif line == self.UNSATISFIABLE:
                raise MiniZincUnsatisfiableError
            elif line == self.UNBOUNDED:
                raise MiniZincUnboundedError
            elif line == self.UNSATorUNBOUNDED:
                raise MiniZincUnsatOrUnboundedError
            elif line == self.ERROR:
                raise MiniZincGenericError
            else:
                _buffer.append(line)
        self.stats = '\n'.join(_buffer)

    def _to_dict(self, stream):
        try:
            while True:
                yield dzn2dict(next(stream))
        except StopIteration as stop:
            return stop.value

