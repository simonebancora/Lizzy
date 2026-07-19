#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.datatypes.solverdata import SolverState

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

class ProgressBar:
    def __init__(self, state:SolverState, total_cvs:int):
        self.total_cvs = total_cvs
        self.state = state
        self.pbar = None
        self._log_redirect = None

    def show(self):
        if self.pbar is None:
            self._log_redirect = logging_redirect_tqdm()
            self._log_redirect.__enter__()
            self.pbar = tqdm(total=self.total_cvs, initial=self.total_cvs - self.state.n_empty_cvs,
                        desc="Fill progress",
                        bar_format="{l_bar}{bar}| t={postfix[0]:.2f}s [{elapsed}<{remaining}]",
                        postfix=[self.state.current_time],
                        ncols=80)

    def update(self, state:SolverState):
        if self.pbar is not None:
            new_filled = self.total_cvs - state.n_empty_cvs
            self.pbar.update(new_filled - self.pbar.n)
            self.pbar.postfix[0] = state.current_time

    def close(self):
        if self.pbar is not None:
            self.pbar.close()
        if self._log_redirect is not None:
            self._log_redirect.__exit__(None, None, None)
            self._log_redirect = None