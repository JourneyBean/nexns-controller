from django.test import TestCase

from django.contrib.auth.models import User
from nexns.variable.models import Variable
from nexns.variable.lib import parse_ip, calculate_ip, get_user_variables_dict, UserVariablesMapping


class TestExpressionHandling(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_ip(self):

        self.assertEqual(
            parse_ip("1.2.3.4"),
            "1.2.3.4",
        )

        self.assertEqual(
            parse_ip("1.2.3.4/24"),
            "1.2.3.0",
        )

        self.assertEqual(
            parse_ip("1.2.3.4/16"),
            "1.2.0.0",
        )

        self.assertEqual(
            parse_ip("1.2.3.4/255.255.255.0"),
            "1.2.3.0",
        )

        self.assertEqual(
            parse_ip("1.2.3.4/255.255.0.0"),
            "1.2.0.0",
        )

        self.assertEqual(
            parse_ip("1.2.3.4/0.0.0.255"),
            "0.0.0.4",
        )

        self.assertEqual(
            parse_ip("1.2.3.4/0.0.255.255"),
            "0.0.3.4",
        )

        self.assertEqual(
            parse_ip("1234:5678:abcd:cdef:fedc:dcba:8765:4321"),
            "1234:5678:abcd:cdef:fedc:dcba:8765:4321",
        )

        self.assertEqual(
            parse_ip("1234::"),
            "1234::",
        )

        self.assertEqual(
            parse_ip("::1234"),
            "::1234",
        )

        self.assertEqual(
            parse_ip("1234:5678:abcd:cdef:fedc:dcba:8765:4321/64"),
            "1234:5678:abcd:cdef::",
        )

        self.assertEqual(
            parse_ip("1234:5678:abcd:cdef:fedc:dcba:8765:4321/56"),
            "1234:5678:abcd:cd00::",
        )

        self.assertEqual(
            parse_ip("1234:5678:abcd:cdef:fedc:dcba:8765:4321/ffff:ffff:ffff:ffff::"),
            "1234:5678:abcd:cdef::",
        )

        self.assertEqual(
            parse_ip("1234:5678:abcd:cdef:fedc:dcba:8765:4321/ffff:ffff::"),
            "1234:5678::",
        )

        self.assertEqual(
            parse_ip("1234:5678:abcd:cdef:fedc:dcba:8765:4321/::ffff:ffff:ffff:ffff"),
            "::fedc:dcba:8765:4321",
        )

        self.assertEqual(
            parse_ip("1234:5678:abcd:cdef:fedc:dcba:8765:4321/::ffff"),
            "::4321",
        )
        
    def test_calculate_ip(self):

        self.assertEqual(
            calculate_ip("1.2.3.4"),
            "1.2.3.4",
        )

        self.assertEqual(
            calculate_ip("1.2.3.4/16 + 1"),
            "1.2.0.1",
        )

        self.assertEqual(
            calculate_ip("1.2.3.4/0.0.0.255 - 1"),
            "0.0.0.3",
        )

        self.assertEqual(
            calculate_ip("2400::+2     -1"),
            "2400::1",
        )

        self.assertEqual(
            calculate_ip("2400::5678/64 + 1234::2345/::ffff"),
            "2400::2345",
        )


class GetUserVarialbesTestCase(TestCase):

    def setUp(self):
        self.data = {
            'ip4_none': '1.2.3.4',
            'ip4_str': '$"1.2.3.4"',
            'ip4_ip': '$`1.2.3.4`',

            'ip4_none_add': '1.2.3.4 + 1',
            'ip4_str_add': '$"1.2.3.4 + 1"',
            'ip4_ip_add': '$`1.2.3.4 + 1`',

            'ip4_var_no_add': '{a}1.2.3.4',
            'ip4_var_str_add': '$"{ip4_none}1.2.3.4"',
            'ip4_var_ip_add1': '$`{ip4_none} + 1.2.3.4`',
            'ip4_var_ip_add2': '$`{ip4_none} + 1`',

            '3numstart': '$`{ip4_none} + 1`',
            '3num_as_var': '$`{3numstart} + 1`',

            'ip6_rt': '$`2400::1234`',
            'ip6_pc': '$`fd00::5678`',
            'public6_pc': '$`{ip6_rt}/64 + {ip6_pc}/::ffff:ffff:ffff:ffff`',
        }
        self.result_data = {
            'ip4_none': '1.2.3.4',
            'ip4_str': '1.2.3.4',
            'ip4_ip': '1.2.3.4',

            'ip4_none_add': '1.2.3.4 + 1',
            'ip4_str_add': '1.2.3.4 + 1',
            'ip4_ip_add': '1.2.3.5',

            'ip4_var_no_add': '{a}1.2.3.4',
            'ip4_var_str_add': '1.2.3.41.2.3.4',
            'ip4_var_ip_add1': '2.4.6.8',
            'ip4_var_ip_add2': '1.2.3.5',

            '3numstart': '1.2.3.5',
            '3num_as_var': '1.2.3.6',

            'ip6_rt': '2400::1234',
            'ip6_pc': 'fd00::5678',
            'public6_pc': '2400::5678',
        }

        User.objects.create_user('test_user', 'test@nexns.io', 'admin@123')
        for k in self.data:
            Variable.objects.create(user_id=1, name=k, text=self.data[k])

    def test_get_user_variables_dict(self):

        m = UserVariablesMapping(1)
        d = dict(m)
        self.assertDictEqual(d, self.data)

        d = get_user_variables_dict(1)
        for key in self.result_data:
            self.assertIn(key, d)
            self.assertEqual(str(d[key]), self.result_data[key])
