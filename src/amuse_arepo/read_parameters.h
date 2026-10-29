/*!
 * \copyright   This file is part of the public version of the AREPO code.
 * \copyright   Copyright (C) 2009-2019, Max-Planck Institute for Astrophysics
 * \copyright   Developed by Volker Springel (vspringel@MPA-Garching.MPG.DE) and
 *              contributing authors.
 * \copyright   Arepo is free software: you can redistribute it and/or modify
 *              it under the terms of the GNU General Public License as published by
 *              the Free Software Foundation, either version 3 of the License, or
 *              (at your option) any later version.
 *
 *              Arepo is distributed in the hope that it will be useful,
 *              but WITHOUT ANY WARRANTY; without even the implied warranty of
 *              MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *              GNU General Public License for more details.
 *
 *              A copy of the GNU General Public License is available under
 *              LICENSE as part of this program.  See also
 *              <https://www.gnu.org/licenses/>.
 *
 * \file        src/io/parameters.c
 * \date        05/2018
 * \brief       Parses the parameter file.
 * \details     This file contains the routine to parse the parameter file.
 *              Additionally the output list is also parsed.
 *              contains functions:
 *                void read_parameter_file(char *fname)
 *                void check_parameters()
 *                int read_outputlist(char *fname)
 *
 * \par Major modifications and contributions:
 *
 * - DD.MM.YYYY Description
 * - 06.05.2018 Prepared file for public release -- Rainer Weinberger
 */

#ifndef PARAM_BRIDGE_H
#define PARAM_BRIDGE_H

#include <map>
#include <string>
#include "interface.h"

extern std::map<std::string, std::string> params;

int build_parameter_schema(
    char tag[MAX_PARAMETERS][MAXLEN_PARAM_TAG],
    void *addr[MAX_PARAMETERS],
    int id[MAX_PARAMETERS]
);

void read_parameter_map(std::map<std::string, std::string> &p);

#ifdef __cplusplus
extern "C" {
#endif

void read_parameter_map_entry(void);

#ifdef __cplusplus
}
#endif

enum {PARAM_REAL = 1, PARAM_STRING = 2, PARAM_INT = 3};  /* must match REAL/STRING/INT in the .cc */

#endif // end PARAM_BRIDGE_H
