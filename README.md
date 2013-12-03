This script is used to process data on Ajustes Diretos (non-bid contracts) from the Portuguese government and prepare it for import into Open Spending (http://openspending.org). This repository serves as an example for other Open Spending efforts.

Source of the data: http://www.base.gov.pt

### Usage:

`python process-ajustes.py [file-name]`

The file-name should be provided without extension.

The script expects the data in a file with one JSON document per line and processes it into a CSV.

### What it does

The script processes mainly the following things:

- all dates are formatted to yyyy-mm-dd;
- whenever the `signing date` is empty, the field is populated with the `publication date`. Openspending discards any row with empty calls;
- the fields containing amounts are stripped from Euro sign and the thousand seperator. The decimal mark is set to `.`;
- the CPV code is split from its description; 
- multiple locations are split with a pipe ` | `; and
- multiple contracting or contracted entities are combined in one new entity. Openspending doesn't allow to have multiple contracting or contracted entities.