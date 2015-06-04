import argparse
import os

from .writer import (
    FastaWriter, PooledFastaWriter,
    FastqWriter, PooledFastqWriter,
    PairedFastqWriter,
    )
from .models import Sample
from .run_file import SequenceFile

writers = {
    "fastq": PairedFastqWriter,
    "fasta": FastaWriter,
    "pooled_fastq": PooledFastqWriter,
    "pooled_fasta": PooledFastaWriter,
    }

def demultiplex(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "--sequence-file", "-s", required=True,
        help="Input sequence data filepath",
        type=argparse.FileType("r"))
    p.add_argument(
        "--barcode-file", "-b", required=True,
        help="Barcode information filepath",
        type=argparse.FileType("r"))
    p.add_argument(
        "--output-dir", "-o", required=True,
        help="Output sequence data directory")
    p.add_argument(
        "--output-format", "-f", required=True,
        help="Output format",
        choices=writers.keys())
    args = p.parse_args(argv)

    seq_file = SequenceFile(args.sequence_file.name)
    samples = list(Sample.load(args.barcode_file))
    
    if os.path.exists(args.output_dir):
        p.error("Output directory already exists")

    os.mkdir(args.output_dir)
    writer_cls = writers[args.output_format]
    writer = writer_cls(samples, args.output_dir)

    read_counts = seq_file.demultiplex(samples, writer)

    demultiplex_log_fp = os.path.join(args.output_dir, "demultiplex_summary.txt")
    with open(demultiplex_log_fp, "w") as f:
        write_demultiplex_summary(f, read_counts)

def write_demultiplex_summary(f, read_counts):
    for sample_id, cts in read_counts.items():
        f.write("%s\t%s\n" % (sample_id, cts))