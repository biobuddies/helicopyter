"""Check the experimental Unicode music renderer with an original scale exercise."""

from fractions import Fraction

from pytest import mark, raises

from helicopyter.music import format_abc, parse_abc, render_abc

scale = 'T:Scale exercise\nM:4/4\nL:1/4\nK:C\nD E F G | A B c d |]'


def test_scale():
    headers, measures = parse_abc(scale)
    assert headers['K'] == 'C'
    assert len(measures) == 2
    assert [note.pitch for note in measures[1].notes] == ['A', 'B', 'c', 'd']
    assert sum(note.duration for note in measures[0].notes) == 1
    assert measures[1].final
    html = render_abc(scale)
    assert html.count('class="music-event"') == 8
    assert html.count('class="music-clef"') == 1
    assert html.count('class="music-meter"') == 1
    assert 'https://raw.githubusercontent.com/google/fonts/main/ofl/notomusic/' in html
    assert 'data:font' not in html
    assert '<svg' not in html
    assert format_abc(scale) == html
    assert render_abc(scale.replace('K:C', 'K:G')).count('class="music-key"') == 1


def test_subdivisions():
    _, measures = parse_abc('M:4/4\nL:1/4\nK:C\nD/ E/ F3/2 G/ A | B2 c2 |')
    assert [note.duration for note in measures[0].notes] == [
        Fraction(1, 8),
        Fraction(1, 8),
        Fraction(3, 8),
        Fraction(1, 8),
        Fraction(1, 4),
    ]


def test_alignment():
    _, measures = parse_abc(scale + '\nw: Step-ping up _ | then~we * come down')
    assert [note.lyric for note in measures[0].notes] == ['Step-', 'ping', 'up', '_']
    assert [note.lyric for note in measures[1].notes] == ['then we', '', 'come', 'down']


@mark.parametrize(
    'source',
    (
        '',
        scale.replace('K:C', 'K:D'),
        scale.replace('M:4/4', 'M:3/4'),
        scale.replace('D E F G', 'D E F'),
        scale.replace('D E F G', '^D E F G'),
        scale.replace('D E F G', '[DE] E F G'),
        scale + '\nD E F G |',
        scale + '\nw: Step-ping',
        scale + '\nw: Step-ping up the scale and down a-gain',
    ),
)
def test_reject_unsupported_notation(source: str):
    with raises(ValueError, match=r'.+'):
        parse_abc(source)
