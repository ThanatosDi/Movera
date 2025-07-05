class Job:
    def __init__(self, include, move_to, filename_regex, rename):
        self.include = include
        self.move_to = move_to
        self.filename_regex = filename_regex
        self.rename = rename

    def __str__(self):
        return f"Job(include='{self.include}', move_to='{self.move_to}', filename_regex='{self.filename_regex}', rename='{self.rename}')"

    def __repr__(self):
        return self.__str__()


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
    def __init__(self, watch_dir, jobs):
        self.watch_dir = watch_dir
        self.jobs = Jobs(jobs)

    def __str__(self):
        return f"Config(watch_dir={self.watch_dir}, jobs={self.jobs})"

    def __repr__(self):
        return self.__str__()
