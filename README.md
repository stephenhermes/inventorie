# inventorie

**inventorie** is a simple inventory management system for DIY electronics. It automatically extracts everything you would want to know about the parts you've ordered, including links to data sheets. At the moment it only supports invoices from [Jameco](www.jameco.com) and [Tayda](www.taydaelectronics.com)--"more" coming "soon."

## Installation

### Dependencies

inventorie requires:
- Python (>= 3.7)
- Java (>= 8)

### User installation

```pip install inventorie```

## Usage

Simply put your invoices (either `.pdf`, or `.eml`) in a folder `workdir` and run 

```
inventorie <workdir> [-o <output.csv>]
``` 
and inventorie will read all the invoices in `workdir`, and spit out the results to `output.csv`. 
