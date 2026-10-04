#!/usr/bin/env bash
export PATH=/workspace/atom-mlmm-g07/reference-env/bin:$PATH
unset PYTHONPATH PIP_CONSTRAINT AMBERHOME
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
