# Set Theory Refresher  

## 1. Premise

Let the universal set be

\[
U=\{0,1,2,\dots,30\}
\]

Define two subsets of \(U\):

\[
A=\{0,2,4,6,8,10,12,14,16,18,20\}
\]

\[
B=\{0,3,6,9,12,15,18,21,24,27,30\}
\]

In words:

- \(A\) is the set of even numbers from \(0\) to \(20\).
- \(B\) is the set of multiples of \(3\) from \(0\) to \(30\).

All set operations below use this same universal set \(U\), set \(A\), and set \(B\).

---

## 2. Core Set Vocabulary

- **Element**: \(x \in A\) means \(x\) is in set \(A\).
- **Not an element**: \(x \notin A\) means \(x\) is not in set \(A\).
- **Subset**: \(A \subseteq B\) means every element of \(A\) is also in \(B\).
- **Empty set**: \(\varnothing\) is the set with no elements.
- **Cardinality**: \(|A|\) is the number of elements in \(A\).

Examples:

\[
2 \in A,\quad 3 \in B,\quad 2 \notin B,\quad 3 \notin A
\]

Neither \(A \subseteq B\) nor \(B \subseteq A\).

---

## 3. Cardinalities

\[
|U| = 31
\]

\[
|A| = 11
\]

\[
|B| = 11
\]

Inclusion–exclusion principle:

\[
|A \cup B| = |A| + |B| - |A \cap B|
\]

---

## 4. Set Operations and Results

### 4.1 Union

\[
A \cup B = \{x : x \in A \text{ or } x \in B\}
\]

\[
A \cup B =
\{0,2,3,4,6,8,9,10,12,14,15,16,18,20,21,24,27,30\}
\]

\[
|A \cup B| = 18
\]

### 4.2 Intersection

\[
A \cap B = \{x : x \in A \text{ and } x \in B\}
\]

The common elements are multiples of both \(2\) and \(3\), i.e. multiples of \(6\):

\[
A \cap B = \{0,6,12,18\}
\]

\[
|A \cap B| = 4
\]

### 4.3 Complement

\[
A^c = U \setminus A
\]

\[
A^c =
\{1,3,5,7,9,11,13,15,17,19,21,22,23,24,25,26,27,28,29,30\}
\]

\[
B^c = U \setminus B
\]

\[
B^c =
\{1,2,4,5,7,8,10,11,13,14,16,17,19,20,22,23,25,26,28,29\}
\]

### 4.4 Set Difference

\[
A \setminus B = \{x : x \in A \text{ and } x \notin B\}
\]

\[
A \setminus B = \{2,4,8,10,14,16,20\}
\]

\[
B \setminus A = \{3,9,15,21,24,27,30\}
\]

### 4.5 Symmetric Difference

\[
A \triangle B = (A \setminus B) \cup (B \setminus A)
\]

\[
A \triangle B =
\{2,3,4,8,9,10,14,15,16,20,21,24,27,30\}
\]

These are the elements in exactly one of \(A\) or \(B\), but not both.

### 4.6 De Morgan’s Laws

\[
(A \cup B)^c = A^c \cap B^c
\]

\[
(A \cap B)^c = A^c \cup B^c
\]

For this example:

\[
(A \cup B)^c =
\{1,5,7,11,13,17,19,22,23,25,26,28,29\}
\]

\[
(A \cap B)^c =
\{1,2,3,4,5,7,8,9,10,11,13,14,15,16,17,19,20,21,22,23,24,25,26,27,28,29,30\}
\]

---

## 5. Venn Diagram Summary

- **Only in \(A\)**:  
  \[
  \{2,4,8,10,14,16,20\}
  \]

- **Only in \(B\)**:  
  \[
  \{3,9,15,21,24,27,30\}
  \]

- **In both \(A\) and \(B\)**:  
  \[
  \{0,6,12,18\}
  \]

- **In neither \(A\) nor \(B\)**:  
  \[
  \{1,5,7,11,13,17,19,22,23,25,26,28,29\}
  \]

---

## 6. Quick Reference Table

| Operation | Notation | Result | Cardinality |
|---|---|---|---|
| Union | \(A \cup B\) | \(\{0,2,3,4,6,8,9,10,12,14,15,16,18,20,21,24,27,30\}\) | 18 |
| Intersection | \(A \cap B\) | \(\{0,6,12,18\}\) | 4 |
| \(A\) minus \(B\) | \(A \setminus B\) | \(\{2,4,8,10,14,16,20\}\) | 7 |
| \(B\) minus \(A\) | \(B \setminus A\) | \(\{3,9,15,21,24,27,30\}\) | 7 |
| Symmetric difference | \(A \triangle B\) | \(\{2,3,4,8,9,10,14,15,16,20,21,24,27,30\}\) | 14 |
| Complement of \(A\) | \(A^c\) | \(\{1,3,5,7,9,11,13,15,17,19,21,22,23,24,25,26,27,28,29,30\}\) | 20 |
| Complement of \(B\) | \(B^c\) | \(\{1,2,4,5,7,8,10,11,13,14,16,17,19,20,22,23,25,26,28,29\}\) | 20 |
| Complement of union | \((A \cup B)^c\) | \(\{1,5,7,11,13,17,19,22,23,25,26,28,29\}\) | 13 |
| Complement of intersection | \((A \cap B)^c\) | \(\{1,2,3,4,5,7,8,9,10,11,13,14,15,16,17,19,20,21,22,23,24,25,26,27,28,29,30\}\) | 27 |

