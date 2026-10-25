#!/bin/bash
sed -i 's/GITHUB_TOKEN: ${{ secrets.GH_PAT }}/GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}/' .github/workflows/discover.yml
sed -i 's/GH_PAT: ${{ secrets.GH_PAT }}/GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}/' .github/workflows/discover.yml
sed -i 's/git push "https:\/\/${{ secrets.GH_PAT }}@github.com\/${{ github.repository }}.git" HEAD:${{ github.ref_name }}/git remote set-url origin https:\/\/x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com\/${{ github.repository }}.git\n          git push origin HEAD:${{ github.ref_name }}/' .github/workflows/discover.yml
