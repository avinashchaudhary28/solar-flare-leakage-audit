# Repeat run (run 6)

The paper uses `results/phase3/` (GitHub Actions run 41008309263).
This folder holds the tables of a second run of the same code on the same inputs
(run 6, triggered by a workflow-file commit). GitHub-hosted runners differ in CPU,
and floating-point results of scikit-learn differ slightly between them:
TSS values differ by up to 0.007, HSS2 by up to 0.02. The tuned-perceptron leakage
interval is +0.004 [-0.002, 0.011] in the paper run and +0.007 [0.001, 0.014] here.
