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
 * \brief       Parses run parameters from an in-memory key-value map.
 * \details     Replaces the file-based parser of the public AREPO release.
 *              Parameters are supplied as a std::map<std::string, std::string>
 *              (e.g. from an embedding/wrapper layer) instead of being read
 *              from a parameter file. The output list is still parsed from file.
 *              contains functions:
 *                int  build_parameter_schema(char tag[][MAXLEN_PARAM_TAG], void *addr[], int id[])
 *                void read_parameter_map(std::map<std::string, std::string> &params)
 *                extern "C" void read_parameter_map_entry(void)
 *
 * \par Major modifications and contributions:
 *
 * - DD.MM.YYYY Description
 * - 06.05.2018 Prepared file for public release -- Rainer Weinberger
 */


// #undef terminate
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <string>
#include <sys/stat.h>
#include <sys/types.h>

#include "interface.h"
#include "read_parameters.h"


/*! \brief Builds the table of recognised parameters.
 *
 *  Fills the tag/address/type tables for all parameters compiled into this
 *  build. Each entry links a parameter name to the member of `All`
 *  that stores its value.
 *
 *  \param[out] tag   Parameter names, null-terminated; shape [MAX_PARAMETERS][MAXLEN_PARAM_TAG].
 *  \param[out] addr  Address of the destination variable in `All`; points to
 *                    double | int | char[] depending on `id`.
 *  \param[out] id    Type code: REAL (1, double) | STRING (2, char[]) | INT (3, int).
 *
 *  \return Number of parameters written to the tables.
 *
 *  \note Caller must provide arrays of size MAX_PARAMETERS; no bounds check is done.
 *  \note REAL, STRING, INT are preprocessor macros defined and undefined within this function.
 */
int build_parameter_schema(
    char tag[MAX_PARAMETERS][MAXLEN_PARAM_TAG],
    void *addr[MAX_PARAMETERS],
    int id[MAX_PARAMETERS])
{
#define REAL 1
#define STRING 2
#define INT 3

  int i;
  int nt = 0;

  std::strcpy(tag[nt], "InitCondFile");
  addr[nt] = All.InitCondFile;
  id[nt++] = STRING;

  std::strcpy(tag[nt], "OutputDir");
  addr[nt] = All.OutputDir;
  id[nt++] = STRING;

#ifdef TOLERATE_WRITE_ERROR
  std::strcpy(tag[nt], "AlternativeOutputDir");
  addr[nt] = AlternativeOutputDir;
  id[nt++] = STRING;
#endif /* #ifdef TOLERATE_WRITE_ERROR */

  std::strcpy(tag[nt], "SnapshotFileBase");
  addr[nt] = All.SnapshotFileBase;
  id[nt++] = STRING;

  std::strcpy(tag[nt], "ResubmitCommand");
  addr[nt] = All.ResubmitCommand;
  id[nt++] = STRING;

  std::strcpy(tag[nt], "OutputListFilename");
  addr[nt] = All.OutputListFilename;
  id[nt++] = STRING;

  std::strcpy(tag[nt], "OutputListOn");
  addr[nt] = &All.OutputListOn;
  id[nt++] = INT;

  std::strcpy(tag[nt], "Omega0");
  addr[nt] = &All.Omega0;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "OmegaBaryon");
  addr[nt] = &All.OmegaBaryon;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "OmegaLambda");
  addr[nt] = &All.OmegaLambda;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "HubbleParam");
  addr[nt] = &All.HubbleParam;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "BoxSize");
  addr[nt] = &All.BoxSize;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "PeriodicBoundariesOn");
  addr[nt] = &All.PeriodicBoundariesOn;
  id[nt++] = INT;

  std::strcpy(tag[nt], "MaxMemSize");
  addr[nt] = &All.MaxMemSize;
  id[nt++] = INT;

  std::strcpy(tag[nt], "TimeOfFirstSnapshot");
  addr[nt] = &All.TimeOfFirstSnapshot;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "CpuTimeBetRestartFile");
  addr[nt] = &All.CpuTimeBetRestartFile;
  id[nt++] = REAL;

#ifdef REDUCE_FLUSH
  std::strcpy(tag[nt], "FlushCpuTimeDiff");
  addr[nt] = &All.FlushCpuTimeDiff;
  id[nt++] = REAL;
#endif /* #ifdef REDUCE_FLUSH */

  std::strcpy(tag[nt], "TimeBetStatistics");
  addr[nt] = &All.TimeBetStatistics;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "TimeBegin");
  addr[nt] = &All.TimeBegin;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "TimeMax");
  addr[nt] = &All.TimeMax;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "TimeBetSnapshot");
  addr[nt] = &All.TimeBetSnapshot;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "UnitVelocity_in_cm_per_s");
  addr[nt] = &All.UnitVelocity_in_cm_per_s;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "UnitLength_in_cm");
  addr[nt] = &All.UnitLength_in_cm;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "UnitMass_in_g");
  addr[nt] = &All.UnitMass_in_g;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "ErrTolIntAccuracy");
  addr[nt] = &All.ErrTolIntAccuracy;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "ErrTolTheta");
  addr[nt] = &All.ErrTolTheta;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "ErrTolForceAcc");
  addr[nt] = &All.ErrTolForceAcc;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "MaxSizeTimestep");
  addr[nt] = &All.MaxSizeTimestep;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "MinSizeTimestep");
  addr[nt] = &All.MinSizeTimestep;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "CourantFac");
  addr[nt] = &All.CourantFac;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "LimitUBelowThisDensity");
  addr[nt] = &All.LimitUBelowThisDensity;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "LimitUBelowCertainDensityToThisValue");
  addr[nt] = &All.LimitUBelowCertainDensityToThisValue;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "DesNumNgb");
  addr[nt] = &All.DesNumNgb;
  id[nt++] = INT;

  std::strcpy(tag[nt], "MultipleDomains");
  addr[nt] = &All.MultipleDomains;
  id[nt++] = INT;

  std::strcpy(tag[nt], "TopNodeFactor");
  addr[nt] = &All.TopNodeFactor;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "ActivePartFracForNewDomainDecomp");
  addr[nt] = &All.ActivePartFracForNewDomainDecomp;
  id[nt++] = REAL;

#ifdef SUBFIND
  std::strcpy(tag[nt], "DesLinkNgb");
  addr[nt] = &All.DesLinkNgb;
  id[nt++] = INT;

  std::strcpy(tag[nt], "ErrTolThetaSubfind");
  addr[nt] = &All.ErrTolThetaSubfind;
  id[nt++] = REAL;
#endif /* #ifdef SUBFIND */

#if defined(ISOTHERM_EQS)
  std::strcpy(tag[nt], "IsoSoundSpeed");
  addr[nt] = &All.IsoSoundSpeed;
  id[nt++] = REAL;
#endif /* #if defined(ISOTHERM_EQS) */

  std::strcpy(tag[nt], "MaxNumNgbDeviation");
  addr[nt] = &All.MaxNumNgbDeviation;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "ComovingIntegrationOn");
  addr[nt] = &All.ComovingIntegrationOn;
  id[nt++] = INT;

  std::strcpy(tag[nt], "ICFormat");
  addr[nt] = &All.ICFormat;
  id[nt++] = INT;

  std::strcpy(tag[nt], "SnapFormat");
  addr[nt] = &All.SnapFormat;
  id[nt++] = INT;

  std::strcpy(tag[nt], "NumFilesPerSnapshot");
  addr[nt] = &All.NumFilesPerSnapshot;
  id[nt++] = INT;

  std::strcpy(tag[nt], "NumFilesWrittenInParallel");
  addr[nt] = &All.NumFilesWrittenInParallel;
  id[nt++] = INT;

  std::strcpy(tag[nt], "ResubmitOn");
  addr[nt] = &All.ResubmitOn;
  id[nt++] = INT;

  std::strcpy(tag[nt], "CoolingOn");
  addr[nt] = &All.CoolingOn;
  id[nt++] = INT;

  std::strcpy(tag[nt], "StarformationOn");
  addr[nt] = &All.StarformationOn;
  id[nt++] = INT;

  std::strcpy(tag[nt], "TypeOfTimestepCriterion");
  addr[nt] = &All.TypeOfTimestepCriterion;
  id[nt++] = INT;

  std::strcpy(tag[nt], "TypeOfOpeningCriterion");
  addr[nt] = &All.TypeOfOpeningCriterion;
  id[nt++] = INT;

  std::strcpy(tag[nt], "TimeLimitCPU");
  addr[nt] = &All.TimeLimitCPU;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "GasSoftFactor");
  addr[nt] = &All.GasSoftFactor;
  id[nt++] = REAL;

  for(i = 0; i < NSOFTTYPES; i++)
    {
      char buf[100];
      std::sprintf(buf, "SofteningComovingType%d", i);
      std::strcpy(tag[nt], buf);
      addr[nt] = &All.SofteningComoving[i];
      id[nt++] = REAL;
    }

  for(i = 0; i < NSOFTTYPES; i++)
    {
      char buf[100];
      std::sprintf(buf, "SofteningMaxPhysType%d", i);
      std::strcpy(tag[nt], buf);
      addr[nt] = &All.SofteningMaxPhys[i];
      id[nt++] = REAL;
    }

  for(i = 0; i < NTYPES; i++)
    {
      char buf[100];
      std::sprintf(buf, "SofteningTypeOfPartType%d", i);
      std::strcpy(tag[nt], buf);
      addr[nt] = &All.SofteningTypeOfPartType[i];
      id[nt++] = INT;
    }

#ifdef ADAPTIVE_HYDRO_SOFTENING
  std::strcpy(tag[nt], "MinimumComovingHydroSoftening");
  addr[nt] = &All.MinimumComovingHydroSoftening;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "AdaptiveHydroSofteningSpacing");
  addr[nt] = &All.AdaptiveHydroSofteningSpacing;
  id[nt++] = REAL;
#endif /* #ifdef ADAPTIVE_HYDRO_SOFTENING */

  std::strcpy(tag[nt], "GravityConstantInternal");
  addr[nt] = &All.GravityConstantInternal;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "InitGasTemp");
  addr[nt] = &All.InitGasTemp;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "MinGasTemp");
  addr[nt] = &All.MinGasTemp;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "MinEgySpec");
  addr[nt] = &All.MinEgySpec;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "MinimumDensityOnStartUp");
  addr[nt] = &All.MinimumDensityOnStartUp;
  id[nt++] = REAL;

#ifdef NODEREFINE_BACKGROUND_GRID
  std::strcpy(tag[nt], "MeanVolume");
  addr[nt] = &All.MeanVolume;
  id[nt++] = REAL;
#endif /* #ifdef NODEREFINE_BACKGROUND_GRID */

#ifndef VORONOI_STATIC_MESH
#ifdef REGULARIZE_MESH_FACE_ANGLE
  std::strcpy(tag[nt], "CellMaxAngleFactor");
  addr[nt] = &All.CellMaxAngleFactor;
  id[nt++] = REAL;
#else  /* #ifdef REGULARIZE_MESH_FACE_ANGLE */
  std::strcpy(tag[nt], "CellShapingFactor");
  addr[nt] = &All.CellShapingFactor;
  id[nt++] = REAL;
#endif /* #ifdef REGULARIZE_MESH_FACE_ANGLE #else */

  std::strcpy(tag[nt], "CellShapingSpeed");
  addr[nt] = &All.CellShapingSpeed;
  id[nt++] = REAL;
#endif /* #ifndef VORONOI_STATIC_MESH */

#if defined(COOLING)
  std::strcpy(tag[nt], "TreecoolFile");
  addr[nt] = &All.TreecoolFile;
  id[nt++] = STRING;
#endif /* #if defined(COOLING) */

#if defined(REFINEMENT)
  std::strcpy(tag[nt], "ReferenceGasPartMass");
  addr[nt] = &All.ReferenceGasPartMass;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "TargetGasMassFactor");
  addr[nt] = &All.TargetGasMassFactor;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "RefinementCriterion");
  addr[nt] = &All.RefinementCriterion;
  id[nt++] = INT;

  std::strcpy(tag[nt], "DerefinementCriterion");
  addr[nt] = &All.DerefinementCriterion;
  id[nt++] = INT;
#endif /* #if defined(REFINEMENT) */

#ifdef USE_SFR
  std::strcpy(tag[nt], "CritOverDensity");
  addr[nt] = &All.CritOverDensity;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "TemperatureThresh");
  addr[nt] = &All.TemperatureThresh;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "CritPhysDensity");
  addr[nt] = &All.CritPhysDensity;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "FactorSN");
  addr[nt] = &All.FactorSN;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "FactorEVP");
  addr[nt] = &All.FactorEVP;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "TempSupernova");
  addr[nt] = &All.TempSupernova;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "TempClouds");
  addr[nt] = &All.TempClouds;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "MaxSfrTimescale");
  addr[nt] = &All.MaxSfrTimescale;
  id[nt++] = REAL;
#endif /* #ifdef USE_SFR */

#ifdef MHD_SEEDFIELD
  std::strcpy(tag[nt], "MHDSeedDir");
  addr[nt] = &All.B_dir;
  id[nt++] = INT;

  std::strcpy(tag[nt], "MHDSeedValue");
  addr[nt] = &All.B_value;
  id[nt++] = REAL;
#endif /* #ifdef MHD_SEEDFIELD */

#ifdef REFINEMENT_VOLUME_LIMIT
  std::strcpy(tag[nt], "MaxVolumeDiff");
  addr[nt] = &All.MaxVolumeDiff;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "MinVolume");
  addr[nt] = &All.MinVolume;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "MaxVolume");
  addr[nt] = &All.MaxVolume;
  id[nt++] = REAL;
#endif /* #ifdef REFINEMENT_VOLUME_LIMIT */

#ifdef TILE_ICS
  std::strcpy(tag[nt], "TileICsFactor");
  addr[nt] = &All.TileICsFactor;
  id[nt++] = INT;
#endif /* #ifdef TILE_ICS */

#ifdef ADDBACKGROUNDGRID
  std::strcpy(tag[nt], "GridSize");
  addr[nt] = &All.GridSize;
  id[nt++] = INT;
#endif /* #ifdef ADDBACKGROUNDGRID */

#ifdef ONEDIMS_SPHERICAL
  std::strcpy(tag[nt], "CoreRadius");
  addr[nt] = &All.CoreRadius;
  id[nt++] = REAL;

  std::strcpy(tag[nt], "CoreMass");
  addr[nt] = &All.CoreMass;
  id[nt++] = REAL;
#endif /* #ifdef ONEDIMS_SPHERICAL */

  return nt;

#undef REAL
#undef STRING
#undef INT
}


/*! \brief Assigns parameters from a key-value map and distributes them to all tasks.
 *
 *  Task 0 builds the schema via build_parameter_schema(), matches each map key
 *  to a schema tag, converts the value, and stores it in `All`. It then verifies
 *  that every schema parameter was set. Afterwards `All` and the
 *  Parameters/ParametersValue/ParametersType arrays are broadcast to all tasks.
 *
 *  \param[in] params Parameter name -> value as string. Names must match schema
 *                    tags exactly (case-sensitive). Only read on task 0.
 *
 *  \return void
 *
 *  \par Error handling:
 *  Calls MPI_Finalize() and exit(errorFlag) on all tasks if, on task 0:
 *  - a key is not in the schema,
 *  - a schema parameter is missing from `params`,
 *  - read_outputlist() fails.
 *
 *  \par Side effects:
 *  - sets `All.StarformationOn = 0` as default,
 *  - allocates Parameters, ParametersValue, ParametersType via mymalloc().
 *
 *  \note Collective: must be called by all MPI tasks.
 *  \note No comment/blank-line handling; the caller must filter the map.
 *  \note Duplicate keys cannot occur in std::map; the "multiply defined" branch
 *        is unreachable.
 *  \note No `-usedvalues` file is written. Unknown tags are never downgraded
 *        to warnings (ALLOWEXTRAPARAMS is not honoured).
 *
 *  \warning Numeric values are not validated (atof/atoi return 0 on malformed input).
 *  \warning `All.OutputDir` is trailing-slash-normalised and mkdir()-ed
 *           unconditionally, even if parsing failed.
 */
void read_parameter_map(std::map<std::string, std::string> &params) {
#define REAL 1
#define STRING 2
#define INT 3

  int i, nt = 0;
  int id[MAX_PARAMETERS];
  void *addr[MAX_PARAMETERS];
  char tag[MAX_PARAMETERS][MAXLEN_PARAM_TAG];
  char buf3[MAXLEN_PARAM_TAG + MAXLEN_PARAM_VALUE + 400];
  int param_handled[MAX_PARAMETERS];
  int errorFlag = 0;

  All.StarformationOn = 0; /* defaults */

  for(i = 0; i < MAX_PARAMETERS; i++)
    {
      param_handled[i] = 0;
    }

  if(sizeof(long long) != 8)
    {
      mpi_terminate("\nType `long long' is not 64 bit on this platform. Stopping.\n\n");
    }

  if(sizeof(int) != 4)
    {
      mpi_terminate("\nType `int' is not 32 bit on this platform. Stopping.\n\n");
    }

  if(sizeof(float) != 4)
    {
      mpi_terminate("\nType `float' is not 32 bit on this platform. Stopping.\n\n");
    }

  if(sizeof(double) != 8)
    {
      mpi_terminate("\nType `double' is not 64 bit on this platform. Stopping.\n\n");
    }

  if(ThisTask == 0) /* read parameter file on process 0 */
    {
      nt = build_parameter_schema(tag, addr, id);

      std::printf("Obtaining parameters from in-memory map:\n\n");

      for(auto &kv : params)
        {
          int j = -1;
          for(i = 0; i < nt; i++)
          {
              if(kv.first == tag[i])
              {
                  if(param_handled[i] == 0)
                  {
                      j = i;
                      param_handled[i] = 1;
                  }
                  else
                    j = -2;
                  break;
              }
          }

          if(j >= 0)
          {
              const char *buf1 = kv.first.c_str();
              const char *buf2 = kv.second.c_str();

              switch(id[j])
              {
                  case REAL:
                    *((double *)addr[j]) = std::atof(buf2);
                    std::sprintf(buf3, "%%-%ds%%g\n", MAXLEN_PARAM_TAG);
                    std::fprintf(stdout, "        ");
                    std::fprintf(stdout, buf3, buf1, *((double *)addr[j]));
                    break;
                  case STRING:
                    std::strncpy((char *)addr[j], buf2, MAXLEN_PARAM_VALUE - 1);
                    ((char *)addr[j])[MAXLEN_PARAM_VALUE - 1] = '\0';
                    std::sprintf(buf3, "%%-%ds%%s\n", MAXLEN_PARAM_TAG);
                    std::fprintf(stdout, "        ");
                    std::fprintf(stdout, buf3, buf1, (char *)addr[j]);
                    break;
                  case INT:
                    *((int *)addr[j]) = std::atoi(buf2);
                    std::sprintf(buf3, "%%-%ds%%d\n", MAXLEN_PARAM_TAG);
                    std::fprintf(stdout, "        ");
                    std::fprintf(stdout, buf3, buf1, *((int *)addr[j]));
                    break;
              }
          }
          else if(j == -2)
          {
              std::fprintf(stdout, "Error: Tag '%s' multiply defined.\n", kv.first.c_str());
              errorFlag = 1;
          }
          else
          {
              std::fprintf(stdout, "Error: Tag '%s' not recognized by this build.\n", kv.first.c_str());
              errorFlag = 1;
          }
        }

      std::printf("\n");

      i = std::strlen(All.OutputDir);
      if(i > 0 && All.OutputDir[i - 1] != '/')
        std::strcat(All.OutputDir, "/");
      mkdir(All.OutputDir, 02755);

      for(i = 0; i < nt; i++)
        {
          if(param_handled[i] != 1)
            {
              std::printf("Error. Missing required parameter '%s'.\n", tag[i]);
              errorFlag = 1;
            }
        }

      if(All.OutputListOn && errorFlag == 0)
        errorFlag += read_outputlist(All.OutputListFilename);
      else
        All.OutputListLength = 0;
    }

  MPI_Bcast(&errorFlag, 1, MPI_INT, 0, MPI_COMM_WORLD);

  if(errorFlag)
    {
      MPI_Finalize();
      exit(errorFlag);
    }

  All.NParameters = nt;

  /* now communicate the relevant parameters to the other processes */
  MPI_Bcast(&All, sizeof(struct global_data_all_processes), MPI_BYTE, 0, MPI_COMM_WORLD);

#ifdef TOLERATE_WRITE_ERROR
  MPI_Bcast(AlternativeOutputDir, MAXLEN_PATH, MPI_BYTE, 0, MPI_COMM_WORLD);
#endif /* #ifdef TOLERATE_WRITE_ERROR */

#ifdef HOST_MEMORY_REPORTING
  check_maxmemsize_setting();
#endif /* #ifdef HOST_MEMORY_REPORTING */

  mymalloc_init();

  Parameters      = (char(*)[MAXLEN_PARAM_TAG])mymalloc("Parameters", All.NParameters * MAXLEN_PARAM_TAG * sizeof(char));
  ParametersValue = (char(*)[MAXLEN_PARAM_VALUE])mymalloc("ParametersValue", All.NParameters * MAXLEN_PARAM_VALUE * sizeof(char));
  // ParametersType  = mymalloc("ParamtersType", All.NParameters * sizeof(char));
  ParametersType = static_cast<char *>(
      mymalloc("ParamtersType", All.NParameters * sizeof(char))
  );

  if(ThisTask == 0)
    {
      for(i = 0; i < All.NParameters; i++)
        {
          std::strncpy(Parameters[i], tag[i], MAXLEN_PARAM_TAG);
          Parameters[i][MAXLEN_PARAM_TAG - 1] = '\0';
          ParametersType[i] = id[i];
          void *tmp         = ParametersValue[i];
          switch(id[i])
            {
              case REAL:
                *static_cast<double *>(tmp) = *static_cast<double *>(addr[i]);
                break;
              case STRING:
                std::strncpy(static_cast<char *>(tmp), static_cast<const char *>(addr[i]), MAXLEN_PARAM_VALUE);
                static_cast<char *>(tmp)[MAXLEN_PARAM_VALUE - 1] = '\0';
                break;
              case INT:
                *static_cast<int *>(tmp) = *static_cast<int *>(addr[i]);
                break;
            }
        }
    }

  MPI_Bcast(Parameters, sizeof(char) * All.NParameters * MAXLEN_PARAM_TAG, MPI_BYTE, 0, MPI_COMM_WORLD);
  MPI_Bcast(ParametersValue, sizeof(char) * All.NParameters * MAXLEN_PARAM_VALUE, MPI_BYTE, 0, MPI_COMM_WORLD);
  MPI_Bcast(ParametersType, sizeof(char) * All.NParameters, MPI_BYTE, 0, MPI_COMM_WORLD);

#undef REAL
#undef STRING
#undef INT
}


/*! \brief C-linkage entry point for read_parameter_map().
 *
 *  Calls read_parameter_map() on the global `params` map.
 *
 *  Notes
 *  -----
 *  - `params` is a global declared outside this file;
 *    it must be populated on task 0 before this call.
 *  - Collective: must be called by all MPI tasks.
 */
extern "C" void read_parameter_map_entry(void)
{
  read_parameter_map(params);
}
