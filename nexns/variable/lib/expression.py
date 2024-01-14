import re
from enum import Enum
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface, AddressValueError

from .exceptions import ParseError


def parse_ip(expression: str) -> str:
    """
    Parse IP address: supports both netmask and hostmask.

    Example:
        1.2.3.4             => 1.2.3.4
        1.2.3.4/24          => 1.2.3.0
        1.2.3.4/255.255.0.0 => 1.2.0.0
        1.2.3.4/0.0.0.255   => 0.0.0.4
        fd12:1234::abcd             => fd12:1234::abcd
        fd12:1234::abcd/64          => fd12:1234::
        fd12:1234::abcd/ffff:ffff:: => fd12:1234::
        fd12:1234::abcd/::ffff      => ::abcd
    """

    expression = expression.strip()
    # IPv4
    if "." in expression:
        parts = expression.split('/')

        # ipv4/ipv4
        if len(parts) == 2 and '.' in parts[1]:
            primary = IPv4Address(parts[0])
            mask = IPv4Address(parts[1])
            return str(IPv4Address(int(primary) & int(mask)))
        # cidr
        else:
            return str(IPv4Interface(expression).network[0])
            
    # IPv6
    elif ":" in expression:
        parts = expression.split('/')

        # ipv6/ipv6
        if len(parts) == 2 and ':' in parts[1]:
            primary = IPv6Address(parts[0])
            mask = IPv6Address(parts[1])
            return str(IPv6Address(int(primary) & int(mask)))
        # cidr
        else:
            return str(IPv6Interface(expression).network[0])

    else:
        raise ParseError(expression, "IP not valid")


def calculate_ip(expression: str) -> str:
    if '+' not in expression and '-' not in expression:
        return parse_ip(expression)
    list = re.split(r'([+-])', expression)

    ipaddress_class = IPv4Address if '.' in expression else IPv6Address
    sum = 0
    op = '+'
    
    for e in list:
        if e == '+' or e == '-':
            op = e
        else:
            try:
                n = int(e)
            except ValueError:
                n = int(ipaddress_class(parse_ip(e)))
                
            if op == '+':
                sum += n
            else:
                sum -= n

    try:
        return str(ipaddress_class(sum))
    except AddressValueError:
        raise ParseError(expression, "IP calculation failed")


class RecordExpression:
    """
    Record Expression processing class

    example:
        assume  a = 1.2.3.4
                b = 1.2.3.4/24
                c = 1.2.3.4/0.0.0.255
                d = $`{a}/24`
                e = abcd

        1.2.3.4     => 1.2.3.4
        1.2.3.4/24  => 1.2.3.4/24

        $`1.2.3.4`              => 1.2.3.4
        $`1.2.3.4/24`           => 1.2.3.0
        $`1.2.3.4/0.0.0.255`    => 0.0.0.4

        $`fe80:1234::5678`          => fe80:1234::5678
        $`fe80:1234::5678/64`       => fe80:1234::
        $`fe80:1234::5678/::ffff`   => ::5678

        $`{a}`              => $`1.2.3.4`           => 1.2.3.4
        $`{a}/24`           => $`1.2.3.4/24`        => 1.2.3.0
        $`{a}/0.0.0.255`    => $`1.2.3.4/0.0.0.255` => 0.0.0.4

        $`{a} + 1`      => $`1.2.3.4 + 1`                       => 1.2.3.5
        $`{b} + {c}`    => $`1.2.3.4/24 + 1.2.3.4/0.0.0.255`    => 1.2.3.4
        $`{a}/24 + 1`   => $`1.2.3.4/24 + 1`                    => 1.2.3.1
        
        $"{e}"          => abcd
        $"{e}1234"      => abcd1234
        $"{a} + 1"      => 1.2.3.4 + 1

        $`{a} + 1`5678  => invalid
        $"{e}1234"5678  => invalid

        $$`{a} + 1`     => $`{a} + 1`
        $$"{e}"         => $"{e}"
    """

    class Type(Enum):
        NONE = 0
        IP = 1
        STR = 2

    def __init__(self, expression: str, variables: dict):
        self.expression = expression
        self.variables = variables
        self.type: RecordExpression.Type = None
        self.parsed = self.parse()

    def parse(self):
        expression= self.expression

        if len(expression) >= 2:

            if expression[0:2] == '$`':
                expression = expression[2:].removesuffix('`')
                self.type = self.Type.IP
                try:
                    expression = expression.format(**self.variables)
                    return calculate_ip(expression)
                except KeyError as e:
                    raise ParseError(self.expression, f"variable {e} not found")
                except ParseError as e:
                    raise e
                
            elif expression[0:2] == '$"':
                expression = expression[2:].removesuffix('"')
                self.type = self.Type.STR
                try:
                    expression = expression.format(**self.variables)
                    return expression
                except KeyError as e:
                    raise ParseError(self.expression, f"variable {e} not found")
                
            elif expression[0:2] == '$$':
                return expression[1:]

            else:
                return expression
            
        return expression

    def __repr__(self) -> str:
        return self.parsed
    