# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Tests for return_statements module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.autograph.converters import return_statements
from tensorflow.python.autograph.core import converter_testing
from tensorflow.python.framework import ops
from tensorflow.python.platform import test


class SingleReturnTest(converter_testing.TestCase):

  def assertTransformedEquivalent(self, test_fn, *inputs):
    ns = {'ops': ops}
    with self.converted(test_fn, return_statements, ns) as result:
      self.assertEqual(test_fn(*inputs), result.test_fn(*inputs))

  def test_straightline(self):

    def test_fn(x):
      return x * x

    self.assertTransformedEquivalent(test_fn, 2)

  def test_conditional(self):

    def test_fn(x):
      if x > 0:
        return x
      else:
        return x * x

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, -2)

  def test_missing_else(self):

    def test_fn(x):
      if x > 0:
        return x

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, -2)

  def test_missing_else_then_default(self):

    def test_fn(x):
      if x > 0:
        return x
      return x * x

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, -2)

  def test_else_only_then_default(self):

    def test_fn(x):
      if x < 0:
        x *= x
      else:
        return x
      return x

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, -2)

  def test_conditional_nested(self):

    def test_fn(x):
      if x > 0:
        if x < 5:
          return x
        else:
          return x * x
      else:
        return x * x * x

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, -2)
    self.assertTransformedEquivalent(test_fn, 5)

  def test_context_manager(self):

    def test_fn(x):
      with ops.name_scope(''):
        return x * x

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, -2)

  def test_context_manager_in_conditional(self):

    def test_fn(x):
      if x > 0:
        with ops.name_scope(''):
          return x * x
      else:
        return x

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, -2)

  def text_conditional_in_context_manager(self):

    def test_fn(x):
      with ops.name_scope(''):
        if x > 0:
          return x * x
        else:
          return x

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, -2)

  def test_no_return(self):

    def test_fn(x):
      x *= x

    self.assertTransformedEquivalent(test_fn, 2)

  def test_nested_function(self):

    def test_fn(x):

      def inner_fn(y):
        if y > 0:
          return y * y
        else:
          return y

      return inner_fn(x)

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, -2)

  def test_nested_function_in_control_flow(self):

    def test_fn(x):

      if x:
        def inner_fn(y):
          return y
        inner_fn(x)

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, -2)

  def test_for_loop(self):

    def test_fn(n):
      for _ in range(n):
        return 1

    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, 0)

  def test_while_loop(self):

    def test_fn(n):
      i = 0
      s = 0
      while i < n:
        i += 1
        s += i
        if s > 4:
          return s
      return -1

    self.assertTransformedEquivalent(test_fn, 0)
    self.assertTransformedEquivalent(test_fn, 2)
    self.assertTransformedEquivalent(test_fn, 4)


if __name__ == '__main__':
  test.main()
