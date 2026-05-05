# Resultados de testes

Data: 05/05/2026

Execucao local:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Resultado:

- `test_solution_a_cancelamento_tem_prioridade`: ok
- `test_solution_b_financeiro`: ok
- `test_solution_c_escalonamento`: ok
- Total: 3 testes, 0 falhas

Benchmark executado:

```bash
python src/run_benchmark.py
```

Artefato gerado:

- `docs/evidence/benchmark-output.json`

