# Copyright (C) 2018-9  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
# email contact: christoph.rosemann@desy.de
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in  version 2
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.

from . import parameterSettingWidget
from PyQt4 import QtGui
import numpy as np
import math


class GaussianParameterSettingWidget(parameterSettingWidget.ParameterSettingWidget):

    def __init__(self, model, xdata, ydata, **kw):
        super(GaussianParameterSettingWidget, self).__init__(**kw)
        self.passData(xdata, ydata)
        self.meanValue.valueChanged.connect(self._updateMean)
        self.meanSlider.valueChanged.connect(self._updateMean)
        self.maximumValue.valueChanged.connect(self._updateMaximum)
        self.maximumSlider.valueChanged.connect(self._updateMaximum)
        self.sigmaValue.valueChanged.connect(self._updateSigma)
        self.sigmaSlider.valueChanged.connect(self._updateSigma)
        self._model = model
        self._parameters = None
        self._modelprefix = str("m" + str(self._name) + "_")
        self._exo.setName(self._modelprefix)
        self._setColour(self._exo.colour())
        self._checkMaxima()
        self.useLBMean.hide()
        self.useUBMean.hide()
        self.meanLBValue.hide()
        self.meanUBValue.hide()
        self.useLBMaximum.hide()
        self.useUBMaximum.hide()
        self.maximumLBValue.hide()
        self.maximumUBValue.hide()
        self.useLBSigma.hide()
        self.useUBSigma.hide()
        self.sigmaLBValue.hide()
        self.sigmaUBValue.hide()
        self.extendButton.clicked.connect(self._togglehide)
        self.chooseColourButton.clicked.connect(self._chooseColour)

    def _togglehide(self):
        if self.useLBMean.isHidden():
            self.useLBMean.show()
            self.useUBMean.show()
            self.meanLBValue.show()
            self.meanUBValue.show()
            self.useLBMaximum.show()
            self.useUBMaximum.show()
            self.maximumLBValue.show()
            self.maximumUBValue.show()
            self.useLBSigma.show()
            self.useUBSigma.show()
            self.sigmaLBValue.show()
            self.sigmaUBValue.show()
            self.extendButton.setText("Shorten")
        else:
            self.useLBMean.hide()
            self.useUBMean.hide()
            self.meanLBValue.hide()
            self.meanUBValue.hide()
            self.useLBMaximum.hide()
            self.useUBMaximum.hide()
            self.maximumLBValue.hide()
            self.maximumUBValue.hide()
            self.useLBSigma.hide()
            self.useUBSigma.hide()
            self.sigmaLBValue.hide()
            self.sigmaUBValue.hide()
            self.extendButton.setText("Extend")

    def _checkMaxima(self):
        datamax = np.amax(self._ydata)
        if self.maximumValue.maximum() <= datamax:
            self.maximumValue.setMaximum(datamax*1000)
            self.maximumUBValue.setMaximum(datamax*1000)

    def _updateSigma(self, value):
        if isinstance(value, int):
            valuewidth = self.sigmaUBValue.value() - self.sigmaLBValue.value()
            currentVal = (self.sigmaSlider.minimum() + float(value * self.sigmaSlider.singleStep()))/(self.sigmaSlider.maximum() - self.sigmaSlider.minimum())
            self.sigmaValue.setValue(self.sigmaLBValue.value() + currentVal*valuewidth)
        else:
            self.sigmaSlider.setValue(round((value - self._sigmaBounds[0])/self.sigmaStep))
        self.updateFit.emit()

    def _updateMaximum(self, value):
        if isinstance(value, int):
            valuewidth = self.maximumUBValue.value() - self.maximumLBValue.value()
            currentVal = (self.maximumSlider.minimum() + value * self.maximumSlider.singleStep())/(self.maximumSlider.maximum() - self.maximumSlider.minimum())
            self.maximumValue.setValue(self.maximumLBValue.value() + currentVal*valuewidth)
        else:
            self.maximumSlider.setValue(round((value - self._maximumBounds[0])/self.maximumStep))
        self.updateFit.emit()

    def _updateMean(self, value=None):
        # ugly as hell, but maybe the only way??: check for type. if int, the call came from slider
        if isinstance(value, int):
            valuewidth = self._meanBounds[1]-self._meanBounds[0]
            currentVal = (self.meanSlider.minimum() + float(value * self.meanSlider.singleStep()))/(self.meanSlider.maximum() - self.meanSlider.minimum())
            self.meanValue.setValue(self._meanBounds[0] + currentVal*valuewidth)
        else:
            self.meanSlider.setValue(round((value - self._meanBounds[0])/self.meanStep))
        self.updateFit.emit()

    def update(self):
        # first basic calculations
        self._meanDisplay = float(np.mean(self._xdata))
        self._meanBounds = (float(np.amin(self._xdata)), float(np.amax(self._xdata)))
        self._sigmaDisplay = float(np.amax(self._xdata) - np.amin(self._xdata))/10.
        self._sigmaBounds = (float(self._sigmaDisplay/25.), float(self._sigmaDisplay*2.))
        self._maximumDisplay = float(np.amax(self._ydata))/2.
        lowerMaxBound = float(np.amin(self._ydata))
        if lowerMaxBound < 0.:
            lowerMaxBound = 0.
        self._maximumBounds = (lowerMaxBound, float(np.amax(self._ydata))*1.2)

        # first fix the accuracy of the display
        # number of steps;
        self.meanStep = (self._meanBounds[1] - self._meanBounds[0])/(self.meanSlider.maximum()-self.meanSlider.minimum())
        self.meanValue.setSingleStep(self.meanStep/5.)
        meanAcc = math.floor(math.fabs(math.log10(self.meanStep)))+2
        self.meanValue.setDecimals(meanAcc)
        self.meanLBValue.setDecimals(meanAcc)
        self.meanUBValue.setDecimals(meanAcc)

        self.maximumStep = (self._maximumBounds[1] - self._maximumBounds[0])/(self.maximumSlider.maximum()-self.maximumSlider.minimum())
        self.maximumValue.setSingleStep(self.maximumStep/5.)
        maximumAcc = math.floor(math.fabs(math.log10(self.maximumStep)))+2
        self.maximumValue.setDecimals(maximumAcc)
        self.maximumLBValue.setDecimals(maximumAcc)
        self.maximumUBValue.setDecimals(maximumAcc)

        self.sigmaStep = (self._sigmaBounds[1] - self._sigmaBounds[0])/(self.sigmaSlider.maximum()-self.sigmaSlider.minimum())
        self.sigmaValue.setSingleStep(self.sigmaStep/5.)
        sigmaAcc = math.floor(math.fabs(math.log10(self.sigmaStep)))+2
        self.sigmaValue.setDecimals(sigmaAcc)
        self.sigmaLBValue.setDecimals(sigmaAcc)
        self.sigmaUBValue.setDecimals(sigmaAcc)

        # first set the boundaries -- as valid for the slider
        # mean:
        self.meanLBValue.setValue(self._meanBounds[0])
        self.meanUBValue.setValue(self._meanBounds[1])
        # amplitude
        self.maximumLBValue.setValue(self._maximumBounds[0])
        self.maximumUBValue.setValue(self._maximumBounds[1])
        # sigma
        self.sigmaLBValue.setValue(self._sigmaBounds[0])
        self.sigmaUBValue.setValue(self._sigmaBounds[1])

        # and now set initial values -- need to be within the boundaries
        self.meanValue.setValue(self._meanDisplay)
        self.maximumValue.setValue(self._maximumDisplay)
        self.sigmaValue.setValue(self._sigmaDisplay)

        self.updateFit.emit()

    def getCurrentFitData(self):
        self._parameters = self._model.make_params(center=self.meanValue.value(),
                                                   amplitude=self._conversionFactorMaximumToAmplitude() * self.maximumValue.value(),
                                                   sigma=self.sigmaValue.value())
        self._exo.setData(self._model.eval(self._parameters, x=self._xdata))
        return self._exo

    def automaticGuess(self):
        print("i'm guessing by the book")

    def getCurrentParameterDict(self):
        centerdict = {}
        centerdict['value'] = self.meanValue.value()
        if(self.meanFixedCB.isChecked()):
            centerdict['vary'] = False
        if(self.useLBMean.isChecked()):
            centerdict['min'] = self.meanLBValue.value()
        if(self.useUBMean.isChecked()):
            centerdict['max'] = self.meanUBValue.value()

        sigmadict = {}
        sigmadict['value'] = self.sigmaValue.value()
        if(self.sigmaFixedCB.isChecked()):
            sigmadict['vary'] = False
        if(self.useLBSigma.isChecked()):
            sigmadict['min'] = self.sigmaLBValue.value()
        if(self.useUBSigma.isChecked()):
            sigmadict['max'] = self.sigmaUBValue.value()

        amplitudedict = {}
        amplitudedict['value'] = self._conversionFactorMaximumToAmplitude() * self.maximumValue.value()
        if(self.maximumFixedCB.isChecked()):
            amplitudedict['vary'] = False
        if (self.useLBMaximum.isChecked()):
            amplitudedict['min'] = self._conversionFactorMaximumToAmplitude() * self.maximumLBValue.value()
        if (self.useUBMaximum.isChecked()):
            amplitudedict['max'] = self._conversionFactorMaximumToAmplitude() * self.maximumUBValue.value()

        pdict = {self._modelprefix:
                 {'modeltype': 'gaussianModel',
                  'center': centerdict,
                  'sigma': sigmadict,
                  'amplitude': amplitudedict,
                  }
                 }
        return pdict

    def getName(self):
        return self._modelName

    def getModel(self):
        return self._model

    def _conversionFactorMaximumToAmplitude(self):
        return math.sqrt(2*math.pi)*self.sigmaValue.value()

    def _chooseColour(self):
        self._qcd = QtGui.QColorDialog()
        self._qcd.show()
        self._qcd.currentColorChanged.connect(self._setColour)

    def _setColour(self, colour):
        self.setColour(colour)
        self.colourDisplay.setStyleSheet(("background-color:"+str(colour.name())))
        self.updateFit.emit()
