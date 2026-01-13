# f90_nml_formatter

A minimal command-line tool for formatting (_well behaved_) FORTRAN namelist files. `f90_nml_formatter` formats a namelist to ensure readable and consistent namelists. 

The tool is based on a regular expression (`\s*,?\s*([^\s=]+)\s*=+(.*)`) for parsing a valid line of a namelist. This means it will not work for any namelist in the wild, but for most well behaved ones.

It offers a few customization options. The default behaviour is formatting the namelist in place.

## Table of contents

1. [Capabilities](#capabilities)
2. [Known Limitations](#known-limitations)
3. [Requirements](#requirements)
4. [Usage](#usage)
5. [Examples](#examples)
6. [Contributing](#contributing)

## Capabilities

* Alignment of `=` based on the longest variable in the whole namelist
* Standardises boolean values to `.true.` and `.false.`
* Standardises quotation marks to `'`
* Unified indentation in blocks
* Unified spacing in lists
* Conversion to lowercase for keys and block names
* Add trailing commas (opt)
* Preserving comments (opt)
* Preserving whitelines in blocks (opt)

## Known Limitations

* No validation of a namelist syntax
* No handling of line continuations
* In place modification

## Requirements

* **Python 3.9.0** or newer as the tool uses modern type hinting syntax

## Usage

No installation required. Simply clone or download the repository and run the script:

```bash
python nml_formatter.py <path_to_namelist_file> [options]
```

### Command-Line Options

```txt
positional arguments:
  namelist              Path to the FORTRAN namelist file to format

optional arguments:
  -h, --help            Show help message and exit
  --output path         Optional output path. If not given, the input namelist is overwritten in place.
  --block-indentation N Number of spaces to indent variables inside a block (default: 2)
  --eq-offset N         Number of spaces after longest key before the '=' sign (default: 5)
  --no-trailing-comma   Remove trailing commas at end of assignments (default: keep them)
  --no-keep-comments    Remove all comments from output (default: keep them)
  --no-keep-whitelines  Remove whitelines inside blocks (default: keep them)
```

## Examples

### 1. Before and After

```fortran
! line comment
&NAMENAME
  variable_long_name = 10.5,

! line comment
short = .TRUE.
  list = 1,2,3
string = "hello world", ! inline comment
  another_var = .f. ! another comment
/
```

----

```fortran
! line comment
&namename
  variable_long_name     = 10.5,

  ! line comment
  short                  = .true.,
  list                   = 1, 2, 3,
  string                 = 'hello world', ! inline comment
  another_var            = .false., ! another comment
/
```

### 2. Before and After

```fortran
! global comment before anything

 &ChEmIsTrY   
 ,dt=60, 
   species='NO2','HCHO',   "O3"
 ,use_fast =.t.,
 max_iter= 100 ,
  threshold=1.0e-6   ! inline comment
 ,rates =  1.0 ,2.0, 3.0
 ,path=   ' /tmp/data '   ! spaces inside string are significant
 ,empty_string='' ,
  weird = .FALSE.
 /

 &meteo
temp=280. 
,pressure= 101325.,
wind_u =5,
  start_month                 =   06,   06,   06,
wind_v=  -3.
 flags = .false.,.true., .f.
 /
```

----

```fortran
! global comment before anything
&chemistry
  dt               = 60,
  species          = 'NO2', 'HCHO', 'O3',
  use_fast         = .true.,
  max_iter         = 100,
  threshold        = 1.0e-6, ! inline comment
  rates            = 1.0, 2.0, 3.0,
  path             = ' /tmp/data ', ! spaces inside string are significant
  empty_string     = '',
  weird            = .false.,
/

&meteo
  temp             = 280.,
  pressure         = 101325.,
  wind_u           = 5,
  start_month      = 06, 06, 06,
  wind_v           = -3.,
  flags            = .false., .true., .false.,
/
```

## Contributing

Contributions are welcome! Feel to submit issues or pull requests.
