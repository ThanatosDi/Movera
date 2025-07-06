class Job:
    def __init__(
        self, include, move_to, src_filename_regex=None, dst_filename_regex=None
    ):
        self.include = include
        self.move_to = move_to
        self.src_filename_regex = src_filename_regex
        self.dst_filename_regex = dst_filename_regex

    def __str__(self):
        return f"Job(include='{self.include}', move_to='{self.move_to}', src_filename_regex='{self.src_filename_regex}', dst_filename_regex='{self.dst_filename_regex}')"

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        return {
            "include": self.include,
            "move_to": self.move_to,
            "src_filename_regex": self.src_filename_regex,
            "dst_filename_regex": self.dst_filename_regex,
        }

    def items(self):
        return self.__dict__().items()


class Jobs:
    def __init__(self, jobs_dict: dict[str, dict]):
        self._jobs: dict[str, Job] = {
            name: Job(**attrs) for name, attrs in jobs_dict.items()
        }

    def __getitem__(self, key: str) -> Job:
        return self._jobs[key]

    def __iter__(self):
        return iter(self._jobs)

    def items(self):
        return self._jobs.items()

    def __str__(self):
        jobs_str = ", ".join([f"'{name}': {job}" for name, job in self._jobs.items()])
        return f"Jobs({{{jobs_str}}})"

    def __repr__(self):
        return self.__str__()


class Config:
    def __init__(self, watches, jobs):
        self.watches = watches
        self.jobs = Jobs(jobs)

    def __str__(self):
        return f"Config(watches={self.watches}, jobs={self.jobs})"

    def __repr__(self):
        return self.__str__()
