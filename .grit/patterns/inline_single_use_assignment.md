---
title: Inline single-use assignment
---

Inline Python assignments that are used exactly once in the following statements.

```grit
engine marzano(0.1)
language python

`$use_stmt` as $use where {
  $use <: after `$x = $e` as $assign,
  $use <: contains `$x`,
  $use <: within module(statements=$stmts),
  $stmts <: not some $other where {
    $other <: contains `$x`,
    $other <: not $use,
    $other <: not `$x = $e`
  },
  $use_stmt <: contains bubble($x, $e) `$x` => $e,
  $assign => .
}
```

## Inline two assignments

```python
wells = ('A01', 'B02')
print(wells)

T8M_90964_c23CT = 'GGCCGAAGGAGACGCTGCAGT'
print(T8M_90964_c23CT)
```

```python

print(('A01', 'B02'))

print('GGCCGAAGGAGACGCTGCAGT')
```

## No assignment to inline

```python
print('A01')
print('B02')
```

## Assignment without same-scope use

```python
wells = ('A01', 'B02')
print('dispensing to plate')
```

## Assignment used twice

```python
# https://pmc.ncbi.nlm.nih.gov/articles/instance/6810757/bin/NIHMS1037790-supplement-supp_info.pdf
T8M_90964_c23CT = 'GGCCGAAGGAGACGCTGCAGT'
print(T8M_90964_c23CT)
log(T8M_90964_c23CT)
```
