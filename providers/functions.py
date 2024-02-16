from typing import Any


def abs(num: float) -> float:
    """
    Returns the absolute value of the given number. In other words, if the number is zero or
    positive then it is returned as-is, but if it is negative then it is multiplied by -1 to make it
    positive before returning it.
    """
    pass


def abspath(path: str) -> str:
    """
    Takes a string containing a filesystem path and converts it to an absolute path. That is, if the
    path is not absolute, it will be joined with the current working directory.
    """
    pass


def alltrue(list: list[bool]) -> bool:
    """
    Returns `true` if all elements in a given collection are `true` or `"true"`. It also returns
    `true` if the collection is empty.
    """
    pass


def anytrue(list: list[bool]) -> bool:
    """
    Returns `true` if any element in a given collection is `true` or `"true"`. It also returns
    `false` if the collection is empty.
    """
    pass


def base64decode(string: str) -> str:
    """
    Takes a string containing a Base64 character sequence and returns the original string.
    """
    pass


def base64encode(string: str) -> str:
    """
    Applies Base64 encoding to a string.
    """
    pass


def base64gzip(string: str) -> str:
    """
    Compresses a string with gzip and then encodes the result in Base64 encoding.
    """
    pass


def base64sha256(string: str) -> str:
    """
    Computes the SHA256 hash of a given string and encodes it with Base64. This is not equivalent to
    `base64encode(sha256("test"))` since `sha256()` returns hexadecimal representation.
    """
    pass


def base64sha512(string: str) -> str:
    """
    Computes the SHA512 hash of a given string and encodes it with Base64. This is not equivalent to
    `base64encode(sha512("test"))` since `sha512()` returns hexadecimal representation.
    """
    pass


def basename(path: str) -> str:
    """
    Takes a string containing a filesystem path and removes all except the last portion from it.
    """
    pass


def bcrypt(string: str) -> str:
    """
    Computes a hash of the given string using the Blowfish cipher, returning a string in [the
    _Modular Crypt Format_](https://passlib.readthedocs.io/en/stable/modular_crypt_format.html)
    usually expected in the shadow password file on many Unix systems.
    """
    pass


def can(expression: Any) -> bool:
    """
    Evaluates the given expression and returns a boolean value indicating whether the expression
    produced a result without any errors.
    """
    pass


def ceil(num: float) -> float:
    """
    Returns the closest whole number that is greater than or equal to the given value, which may be
    a fraction.
    """
    pass


def chomp(string: str) -> str:
    """
    Removes newline characters at the end of a string.
    """
    pass


def chunklist(
    list: list[Any],
    #: The maximum length of each chunk. All but the last element of the result is guaranteed to be
    #: of exactly this size.
    size: float,
) -> list[list[Any]]:
    """
    Splits a single list into fixed-size chunks, returning a list of lists.
    """
    pass


def cidrhost(
    #: `prefix` must be given in CIDR notation, as defined in [RFC 4632 section
    #: 3.1](https://tools.ietf.org/html/rfc4632#section-3.1).
    prefix: str,

    #: `hostnum` is a whole number that can be represented as a binary integer with no more than the
    #: number of digits remaining in the address after the given prefix.
    hostnum: float,
) -> str:
    """
    Calculates a full host IP address for a given host number within a given IP network address
    prefix.
    """
    pass


def cidrnetmask(
    #: `prefix` must be given in CIDR notation, as defined in [RFC 4632 section
    #: 3.1](https://tools.ietf.org/html/rfc4632#section-3.1).
    prefix: str,
) -> str:
    """
    Converts an IPv4 address prefix given in CIDR notation into a subnet mask address.
    """
    pass


def cidrsubnet(
    #: `prefix` must be given in CIDR notation, as defined in [RFC 4632 section
    #: 3.1](https://tools.ietf.org/html/rfc4632#section-3.1).
    prefix: str,

    #: `newbits` is the number of additional bits with which to extend the prefix.
    newbits: float,

    #: `netnum` is a whole number that can be represented as a binary integer with no more than
    #: `newbits` binary digits, which will be used to populate the additional bits added to the
    #: prefix.
    netnum: float,
) -> str:
    """
    Calculates a subnet address within given IP network address prefix.
    """
    pass


def cidrsubnets(
    #: `prefix` must be given in CIDR notation, as defined in [RFC 4632 section
    #: 3.1](https://tools.ietf.org/html/rfc4632#section-3.1).
    prefix: str,
) -> list[str]:
    """
    Calculates a sequence of consecutive IP address ranges within a particular CIDR prefix.
    """
    pass


def coalesce() -> Any:
    """
    Takes any number of arguments and returns the first one that isn't null or an empty string.
    """
    pass


def coalescelist() -> Any:
    """
    Takes any number of list arguments and returns the first one that isn't empty.
    """
    pass


def compact(list: list[str]) -> list[str]:
    """
    Takes a list of strings and returns a new list with any empty string elements removed.
    """
    pass


def concat() -> Any:
    """
    Takes two or more lists and combines them into a single list.
    """
    pass


def contains(list: Any, value: Any) -> Any:
    """
    Determines whether a given list or set contains a given single value as one of its elements.
    """
    pass


def csvdecode(string: str) -> Any:
    """
    Decodes a string containing CSV-formatted data and produces a list of maps representing that
    data.
    """
    pass


def dirname(path: str) -> str:
    """
    Takes a string containing a filesystem path and removes the last portion from it.
    """
    pass


def distinct(list: list[Any]) -> list[Any]:
    """
    Takes a list and returns a new list with any duplicate elements removed.
    """
    pass


def element(list: Any, index: float) -> Any:
    """
    Retrieves a single element from a list.
    """
    pass


def endswith(string: str, suffix: str) -> bool:
    """
    Takes two values: a string to check and a suffix string. The function returns true if the first
    string ends with that exact suffix.
    """
    pass


def file(path: str) -> str:
    """
    Reads the contents of a file at the given path and returns them as a string.
    """
    pass


def filebase64(path: str) -> str:
    """
    Reads the contents of a file at the given path and returns them as a base64-encoded string.
    """
    pass


def filebase64sha256(path: str) -> str:
    """
    Is a variant of `base64sha256` that hashes the contents of a given file rather than a literal
    string.
    """
    pass


def filebase64sha512(path: str) -> str:
    """
    Is a variant of `base64sha512` that hashes the contents of a given file rather than a literal
    string.
    """
    pass


def fileexists(path: str) -> bool:
    """
    Determines whether a file exists at a given path.
    """
    pass


def filemd5(path: str) -> str:
    """
    Is a variant of `md5` that hashes the contents of a given file rather than a literal string.
    """
    pass


def fileset(path: str, pattern: str) -> set[str]:
    """
    Enumerates a set of regular file names given a path and pattern. The path is automatically
    removed from the resulting set of file names and any result still containing path separators
    always returns forward slash (`/`) as the path separator for cross-system compatibility.
    """
    pass


def filesha1(path: str) -> str:
    """
    Is a variant of `sha1` that hashes the contents of a given file rather than a literal string.
    """
    pass


def filesha256(path: str) -> str:
    """
    Is a variant of `sha256` that hashes the contents of a given file rather than a literal string.
    """
    pass


def filesha512(path: str) -> str:
    """
    Is a variant of `sha512` that hashes the contents of a given file rather than a literal string.
    """
    pass


def flatten(list: Any) -> Any:
    """
    Takes a list and replaces any elements that are lists with a flattened sequence of the list
    contents.
    """
    pass


def floor(num: float) -> float:
    """
    Returns the closest whole number that is less than or equal to the given value, which may be a
    fraction.
    """
    pass


def format(format: str) -> Any:
    """
    The function produces a string by formatting a number of other values according to a
    specification string. It is similar to the `printf` function in C, and other similar functions
    in other programming languages.
    """
    pass


def formatdate(format: str, time: str) -> str:
    """
    Converts a timestamp into a different time format.
    """
    pass


def formatlist(format: str) -> Any:
    """
    Produces a list of strings by formatting a number of other values according to a specification
    string.
    """
    pass


def indent(
    #: Number of spaces to add after each newline character.
    spaces: float,

    string: str,) -> str:
    """
    Adds a given number of spaces to the beginnings of all but the first line in a given multi-line
    string.
    """
    pass


def index(list: Any, value: Any) -> Any:
    """
    Finds the element index for a given value in a list.
    """
    pass


def join(
    #: Delimiter to insert between the given strings.
    separator: str,
) -> str:
    """
    Produces a string by concatenating together all elements of a given list of strings with the
    given delimiter.
    """
    pass


def jsondecode(string: str) -> Any:
    """
    Interprets a given string as JSON, returning a representation of the result of decoding that
    string.
    """
    pass


def jsonencode(val: Any) -> str:
    """
    Encodes a given value to a string using JSON syntax.
    """
    pass


def keys(
    #: The map to extract keys from. May instead be an object-typed value, in which case the result
    #: is a tuple of the object attributes.
    inputMap: Any,
) -> Any:
    """
    Takes a map and returns a list containing the keys from that map.
    """
    pass


def length(value: Any) -> float:
    """
    Determines the length of a given list, map, or string.
    """
    pass


def log(num: float, base: float) -> float:
    """
    Returns the logarithm of a given number in a given base.
    """
    pass


def lookup(inputMap: Any, key: str) -> Any:
    """
    Retrieves the value of a single element from a map, given its key. If the given key does not
    exist, the given default value is returned instead.
    """
    pass


def lower(string: str) -> str:
    """
    Converts all cased letters in the given string to lowercase.
    """
    pass


def matchkeys(values: list[Any], keys: list[Any], searchset: list[Any]) -> list[Any]:
    """
    Constructs a new list by taking a subset of elements from one list whose indexes match the
    corresponding indexes of values in another list.
    """
    pass


def max() -> float:
    """
    Takes one or more numbers and returns the greatest number from the set.
    """
    pass


def md5(string: str) -> str:
    """
    Computes the MD5 hash of a given string and encodes it with hexadecimal digits.
    """
    pass


def merge() -> Any:
    """
    Takes an arbitrary number of maps or objects, and returns a single map or object that contains a
    merged set of elements from all arguments.
    """
    pass


def min() -> float:
    """
    Takes one or more numbers and returns the smallest number from the set.
    """
    pass


def nonsensitive(value: Any) -> Any:
    """
    Takes a sensitive value and returns a copy of that value with the sensitive marking removed,
    thereby exposing the sensitive value.
    """
    pass


def one(list: Any) -> Any:
    """
    Takes a list, set, or tuple value with either zero or one elements. If the collection is empty,
    returns `null`. Otherwise, returns the first element. If there are two or more elements then
    will return an error.
    """
    pass


def parseint(number: Any, base: float) -> Any:
    """
    Parses the given string as a representation of an integer in the specified base and returns the
    resulting number. The base must be between 2 and 62 inclusive.
    """
    pass


def pathexpand(path: str) -> str:
    """
    Takes a filesystem path that might begin with a `~` segment, and if so it replaces that segment
    with the current user's home directory path.
    """
    pass


def plantimestamp() -> str:
    """
    Returns a UTC timestamp string in [RFC 3339](https://tools.ietf.org/html/rfc3339) format, fixed
    to a constant time representing the time of the plan.
    """
    pass


def pow(num: float, power: float) -> float:
    """
    Calculates an exponent, by raising its first argument to the power of the second argument.
    """
    pass


def range() -> list[float]:
    """
    Generates a list of numbers using a start value, a limit value, and a step value.
    """
    pass


def regex(pattern: str, string: str) -> Any:
    """
    Applies a [regular expression](https://en.wikipedia.org/wiki/Regular_expression) to a string and
    returns the matching substrings.
    """
    pass


def regexall(pattern: str, string: str) -> list[Any]:
    """
    Applies a [regular expression](https://en.wikipedia.org/wiki/Regular_expression) to a string and
    returns a list of all matches.
    """
    pass


def replace(string: str, substr: str, replace: str) -> str:
    """
    Searches a given string for another given substring, and replaces each occurrence with a given
    replacement string.
    """
    pass


def reverse(list: Any) -> Any:
    """
    Takes a sequence and produces a new sequence of the same length with all of the same elements as
    the given sequence but in reverse order.
    """
    pass


def rsadecrypt(ciphertext: str, privatekey: str) -> str:
    """
    Decrypts an RSA-encrypted ciphertext, returning the corresponding cleartext.
    """
    pass


def sensitive(value: Any) -> Any:
    """
    Takes any value and returns a copy of it marked so that Terraform will treat it as sensitive,
    with the same meaning and behavior as for [sensitive input
    variables](/language/values/variables#suppressing-values-in-cli-output).
    """
    pass


def setintersection(first_set: set[Any]) -> set[Any]:
    """
    The function takes multiple sets and produces a single set containing only the elements that all
    of the given sets have in common. In other words, it computes the
    [intersection](https://en.wikipedia.org/wiki/Intersection_\(set_theory\)) of the sets.
    """
    pass


def setproduct() -> Any:
    """
    The function finds all of the possible combinations of elements from all of the given sets by
    computing the [Cartesian product](https://en.wikipedia.org/wiki/Cartesian_product).
    """
    pass


def setsubtract(a: set[Any], b: set[Any]) -> set[Any]:
    """
    The function returns a new set containing the elements from the first set that are not present
    in the second set. In other words, it computes the [relative
    complement](https://en.wikipedia.org/wiki/Complement_\(set_theory\)#Relative_complement) of the
    second set.
    """
    pass


def setunion(first_set: set[Any]) -> set[Any]:
    """
    The function takes multiple sets and produces a single set containing the elements from all of
    the given sets. In other words, it computes the
    [union](https://en.wikipedia.org/wiki/Union_\(set_theory\)) of the sets.
    """
    pass


def sha1(string: str) -> str:
    """
    Computes the SHA1 hash of a given string and encodes it with hexadecimal digits.
    """
    pass


def sha256(string: str) -> str:
    """
    Computes the SHA256 hash of a given string and encodes it with hexadecimal digits.
    """
    pass


def sha512(string: str) -> str:
    """
    Computes the SHA512 hash of a given string and encodes it with hexadecimal digits.
    """
    pass


def signum(num: float) -> float:
    """
    Determines the sign of a number, returning a number between -1 and 1 to represent the sign.
    """
    pass


def slice(list: Any, start_index: float, end_index: float) -> Any:
    """
    Extracts some consecutive elements from within a list.
    """
    pass


def sort(list: list[str]) -> list[str]:
    """
    Takes a list of strings and returns a new list with those strings sorted lexicographically.
    """
    pass


def split(separator: str, string: str) -> list[str]:
    """
    Produces a list by dividing a given string at all occurrences of a given separator.
    """
    pass


def startswith(string: str, prefix: str) -> bool:
    """
    Takes two values: a string to check and a prefix string. The function returns true if the string
    begins with that exact prefix.
    """
    pass


def strcontains(string: str, substr: str) -> bool:
    """
    Takes two values: a string to check and an expected substring. The function returns true if the
    string has the substring contained within it.
    """
    pass


def strrev(string: str) -> str:
    """
    Reverses the characters in a string. Note that the characters are treated as _Unicode
    characters_ (in technical terms, Unicode [grapheme cluster
    boundaries](https://unicode.org/reports/tr29/#Grapheme_Cluster_Boundaries) are respected).
    """
    pass


def substr(string: str, offset: float, length: float) -> str:
    """
    Extracts a substring from a given string by offset and (maximum) length.
    """
    pass


def sum(list: Any) -> Any:
    """
    Takes a list or set of numbers and returns the sum of those numbers.
    """
    pass


def templatefile(path: str, vars: Any) -> Any:
    """
    Reads the file at the given path and renders its content as a template using a supplied set of
    template variables.
    """
    pass


def textdecodebase64(source: str, encoding: str) -> str:
    """
    Function decodes a string that was previously Base64-encoded, and then interprets the result as
    characters in a specified character encoding.
    """
    pass


def textencodebase64(string: str, encoding: str) -> str:
    """
    Encodes the unicode characters in a given string using a specified character encoding, returning
    the result base64 encoded because Terraform language strings are always sequences of unicode
    characters.
    """
    pass


def timeadd(timestamp: str, duration: str) -> str:
    """
    Adds a duration to a timestamp, returning a new timestamp.
    """
    pass


def timecmp(timestamp_a: str, timestamp_b: str) -> float:
    """
    Compares two timestamps and returns a number that represents the ordering of the instants those
    timestamps represent.
    """
    pass


def timestamp() -> str:
    """
    Returns a UTC timestamp string in [RFC 3339](https://tools.ietf.org/html/rfc3339) format.
    """
    pass


def title(string: str) -> str:
    """
    Converts the first letter of each word in the given string to uppercase.
    """
    pass


def tobool(v: Any) -> bool:
    """
    Converts its argument to a boolean value.
    """
    pass


def tolist(v: Any) -> list[Any]:
    """
    Converts its argument to a list value.
    """
    pass


def tomap(v: Any) -> dict[Any]:
    """
    Converts its argument to a map value.
    """
    pass


def tonumber(v: Any) -> float:
    """
    Converts its argument to a number value.
    """
    pass


def toset(v: Any) -> set[Any]:
    """
    Converts its argument to a set value.
    """
    pass


def tostring(v: Any) -> str:
    """
    Converts its argument to a string value.
    """
    pass


def transpose(values: dict[list[str]]) -> dict[list[str]]:
    """
    Takes a map of lists of strings and swaps the keys and values to produce a new map of lists of
    strings.
    """
    pass


def trim(
    string: str,
    #: A string containing all of the characters to trim. Each character is taken separately, so the
    #: order of characters is insignificant.
    cutset: str,
) -> str:
    """
    Removes the specified set of characters from the start and end of the given string.
    """
    pass


def trimprefix(string: str, prefix: str) -> str:
    """
    Removes the specified prefix from the start of the given string. If the string does not start
    with the prefix, the string is returned unchanged.
    """
    pass


def trimspace(string: str) -> str:
    """
    Removes any space characters from the start and end of the given string.
    """
    pass


def trimsuffix(string: str, suffix: str) -> str:
    """
    Removes the specified suffix from the end of the given string.
    """
    pass


def try_() -> Any:
    """
    Evaluates all of its argument expressions in turn and returns the result of the first one that
    does not produce any errors.
    """
    pass


def upper(string: str) -> str:
    """
    Converts all cased letters in the given string to uppercase.
    """
    pass


def urlencode(string: str) -> str:
    """
    Applies URL encoding to a given string.
    """
    pass


def uuid() -> str:
    """
    Generates a unique identifier string.
    """
    pass


def uuidv5(namespace: str, name: str) -> str:
    """
    Generates a _name-based_ UUID, as described in [RFC 4122 section
    4.3](https://tools.ietf.org/html/rfc4122#section-4.3), also known as a "version 5" UUID.
    """
    pass


def values(mapping: Any) -> Any:
    """
    Takes a map and returns a list containing the values of the elements in that map.
    """
    pass


def yamldecode(src: str) -> Any:
    """
    Parses a string as a subset of YAML, and produces a representation of its value.
    """
    pass


def yamlencode(value: Any) -> str:
    """
    Encodes a given value to a string using [YAML 1.2](https://yaml.org/spec/1.2/spec.html) block
    syntax.
    """
    pass


def zipmap(keys: list[str], values: Any) -> Any:
    """
    Constructs a map from a list of keys and a corresponding list of values.
    """
    pass

