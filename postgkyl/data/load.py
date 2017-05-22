#!/usr/bin/env python
"""
Postgkyl sub-module to load and save G* data
"""
import numpy
import os
import glob


class GData:
    """Provide interface to read output data.

    __init__(fName : string)
    Determine the data type and call the appropriate load function

    Methods:
    _loadG1h5 -- Load G1 HDF5 file
    _loadG2bp -- Load G2 Adios binary file
    """

    def __init__(self, fName, load=True):
        """Determine the data type and call the appropriate load
        function

        Parameters:
        fName -- file name

        Raises:
        NameError -- when specified file is not found
        NameError -- when file extension is neither h5 or bp

        Notes:
        Load function is determined based on the extension
        """
        self.fName = fName
        if not os.path.exists(self.fName):
            raise NameError(
                "GData: File {} does not exist!".format(fName))
        # Parse the file name and select the last part (extension)
        ext = self.fName.split('.')[-1]
        if ext == 'h5':
            self._loadHeaderH5()
            if load:
                self.loadDataH5()
        elif ext == 'bp':
            self._loadHeaderBP()
            if load:
                self.loadDataBP()
        else:
            raise NameError(
                "GData: File extension {} is not supported.".format(ext))

    def __del__(self):
        ext = self.fName.split('.')[-1]
        if ext == 'h5':
            # close the opened file
            self.fh.close()

    def _loadHeaderH5(self):
        """Load a header of a HDF5 file"""
        import tables

        self.fh = tables.open_file(self.fName, 'r')
        grid = self.fh.root.StructGrid

        # read in information about grid
        self.lowerBounds = numpy.array(grid._v_attrs.vsLowerBounds)
        self.upperBounds = numpy.array(grid._v_attrs.vsUpperBounds)
        self.numCells = numpy.array(grid._v_attrs.vsNumCells)
        self.numDims = len(self.numCells)

        # read in time data if it exists
        try:
            self.time = numpy.float(fh.root.timeData._v_attrs.vsTime)
        except:
            self.time = numpy.float(0.0)

    def loadDataH5(self):
        """Load data from a HDF5 file"""
        import tables

        self.q = numpy.array(self.fh.root.StructGridField)

        if len(self.q.shape) > self.numDims:
            self.numComponents = self.q.shape[-1]
        else:
            self.numComponents = 1

    def _loadHeaderBP(self):
        """Load a header of an ADIOS file"""
        import adios

        fh = adios.file(self.fName)

        # read in information about grid
        # Note: when atribute is a scalar, ADIOS only returns standart
        # Python float; for consistency, those are turned into 1D
        # numpy arrays
        self.lowerBounds = numpy.array(adios.attr(fh, 'lowerBounds').value)
        if self.lowerBounds.ndim == 0:
            self.lowerBounds = numpy.expand_dims(self.lowerBounds, 0)
        self.upperBounds = numpy.array(adios.attr(fh, 'upperBounds').value)
        if self.upperBounds.ndim == 0:
            self.upperBounds = numpy.expand_dims(self.upperBounds, 0)
        self.numCells = numpy.array(adios.attr(fh, 'numCells').value)
        if self.numCells.ndim == 0:
            self.numCells = numpy.expand_dims(self.numCells, 0)
        self.numDims = len(self.numCells)

        # read in time data if it exists
        try:
            self.time = numpy.float(adios.readvar(self.fName, 'time'))
        except:
            self.time = numpy.float(0.0)

    def loadDataBP(self):
        """Load data from an ADIOS file"""
        import adios

        self.q = adios.readvar(self.fName, 'CartGridField')

        if len(self.q.shape) > self.numDims:
            self.numComponents = self.q.shape[-1]
        else:
            self.numComponents = 1

class GHistoryData:
    """Provide interface to read history data.

    __init__(fNameRoot : string)
    Determine the data type and call the appropriate load function

    Methods:
    _loadG1h5 -- Load G1 HDF5 files
    _loadG2bp -- Load G2 Adios binary files
    save      -- Save loaded data to a text file
    """

    def __init__(self, fNameRoot, start=0):
        """Determine the data type and call the appropriate load
        function

        Inputs:
        fNameRoot -- file name root

        Raises:
        NameError -- when files with root don't exis
        NameError -- when file extension is neither h5 or bp

        Notes:
        Load function is determined based on the extension
        """
        self.fNameRoot = fNameRoot
        self.files = glob.glob('{}*'.format(self.fNameRoot))
        for fl in self.files:
            ext = fl.split('.')[-1]
            if ext != 'h5' and ext != 'bp':
                self.files.remove(fl)
        if self.files == []:
            raise NameError(
                'GHistoryData: Files with root \'{}\' do not exist!'.
                format(self.fNameRoot))

        # Parse the file name and select the last part (extension)
        ext = self.files[start].split('.')[-1]
        if ext == 'h5':
            self._loadG1h5(start)
        elif ext == 'bp':
            self._loadG2bp(start)
        else:
            raise NameError(
                "GData: File extension {} is not supported.".format(ext))

    def _loadG1h5(self, start):
        """Load the G1 HDF5 history data file"""
        import tables

        # read the first history file
        fh = tables.open_file(self.files[start], 'r')
        self.values = numpy.array(fh.root.DataStruct.data.read())
        self.time = numpy.array(fh.root.DataStruct.timeMesh.read())
        self.time = numpy.squeeze(self.time)
        fh.close()
        # read the rest of the files and append
        for fl in self.files[start+1 :]:
            ext = fl.split('.')[-1]
            if ext == 'h5':
                fh = tables.open_file(fl, 'r')
                self.values = numpy.append(self.values,
                                           fh.root.DataStruct.data.read(), axis=0)
                self.time = numpy.append(self.time,
                                         fh.root.DataStruct.timeMesh.read())
                fh.close()

        # sort with scending time
        sortIdx = numpy.argsort(self.time)
        self.time = self.time[sortIdx]
        self.values = self.values[sortIdx]

        # convert to numpy arrays
        self.values = numpy.array(self.values)
        self.time = numpy.array(self.time)

    def _loadG2bp(self, start):
        """Load the G2 ADIOS history data file"""
        import adios

        # read the first history file                     
        self.values = adios.readvar(self.files[start], 'Data')
        self.time = adios.readvar(self.files[start], 'TimeMesh')
    
        # read the rest of the files and append
        for fl in self.files[start+1 :]:
            ext = fl.split('.')[-1]
            if ext == 'bp':
                self.values = numpy.append(self.values,
                                           adios.readvar(fl, 'Data'),
                                           axis=0)
                self.time = numpy.append(self.time,
                                         adios.readvar(fl, 'TimeMesh'),
                                         axis=0)

        # sort with scending time
        sortIdx = numpy.argsort(self.time)
        self.time = self.time[sortIdx]
        self.values = self.values[sortIdx]

        # convert to numpy arrays
        self.values = numpy.array(self.values)
        self.time = numpy.array(self.time)

    def save(self, fName=None):
        """Write loaded history data to one text file

        Parameters:
        fName (optional) -- specify the output file name

        Note:
        If the 'fName' is not specified, 'fNameRoot' is used instead
        to construct a file name
        """
        if fName is None:
            fName = '{:s}/{:s}.dat'.format(os.getcwd(), self.fNameRoot)

        out = numpy.vstack([self.time, self.values]).transpose()
        numpy.savetxt(fName, out)
