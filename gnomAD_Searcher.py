#! /usr/bin/python3
import os
import sys
import requests
import pandas as pd
import click

@click.command()
@click.option('-i', '--input', required=True, type=click.Path(exists=True, dir_okay=False), help='input file which contains rsid list(column name: rsID)')
def cli(input):
    """ HJ Kim's gnomAD Searcher """

    searcher = gnomAD_Searcher(snplist = input)

class gnomAD_Searcher:
    """gnomAD Database(from myvariant info) 에서 snp의  population별 frequency를 가져온다
       snp은 'rsID'를 컬럼이름 으로 갖고 형식은 'rs123' 또는 'chr15:g.75077367C>A' 형식이 가능하다.
       'rs123'형식으로 찾았을때 못찾는 경우가 있으니 후자쪽을 추천한다."""

    def __init__(snplist):
        snplist = os.path.abspath(snplist)
        df = pd.read_csv(snplist, sep = '\t')
        rsid = df.rsID.to_list()
    
        result = dict()
        for snp in rsid:
            r = requests.get("http://myvariant.info/v1/variant/"+snp+"?fields=gnomad_genome")
            if not r.ok:
                print(snp, "No RESULT")
                continue
            decoded = r.json()
            result.setdefault("rsid", []).append(decoded['gnomad_genome']['rsid'])
            result.setdefault("REF", []).append(decoded['gnomad_genome']['ref'])
            result.setdefault("ALT", []).append(decoded['gnomad_genome']['alt'])
            result.setdefault("African", []).append(decoded['gnomad_genome']['af']['af_afr'])
            result.setdefault("Latino", []).append(decoded['gnomad_genome']['af']['af_amr'])
            result.setdefault("East_Asian", []).append(decoded['gnomad_genome']['af']['af_eas'])
            result.setdefault("Finnish", []).append(decoded['gnomad_genome']['af']['af_fin'])
            result.setdefault("European", []).append(decoded['gnomad_genome']['af']['af_nfe'])

        result_df = pd.DataFrame(result)
        directory = os.path.dirname(snplist)
        filename = os.path.basename(snplist).split('.')[0]
        
        output = os.path.join(directory, f'{filename}_gnomAD_population_freq.txt')
        result_df.to_csv(output, sep='\t', index = False)


if __name__ == '__main__':
    cli()