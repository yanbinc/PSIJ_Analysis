#!python3
"""
PSIJ test bench
@Original author: Yanbin Chen<yanbin_c@hotmail.com>
@Original date:   Feb 22, 2019
Copyright (c) 2019; all rights reserved .
"""
thisProgram = 'PSIJ_analysis_wx_version_no_thread_0p5.py'
revVersion = '0.5'
revDate = '2019-02-24'
revAuthor='yanbin_c'
revCompany='Non'

import  os
import sys
import time,datetime
import openpyxl
import logging
import  wx
import  wx.lib.filebrowsebutton as filebrowse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from time import clock
#logging.basicConfig(level=logging.DEBUG,format=' %(asctime)s- %(levelname)s- %(message)s')
logging.basicConfig(level=logging.INFO)
#logging.disable(logging.CRITICAL)
#logging.basicConfig(filename='log.txt',level=logging.DEBUG,format=' %(asctime)s- %(levelname)s- %(message)s')
import ychen_class_psij_v0p5 as C_PSIJ

plt_dic={}
plt_dic["program"]=thisProgram
plt_dic["version"]=revVersion
plt_dic["v_data"]=revDate
plt_dic["author"]=revAuthor
plt_dic["company"]=revCompany

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,-1,'PSIJ Analysis v'+revVersion,size=(650,420))
        nb_main=wx.Notebook(self,-1,pos=(0,0),size=(650,420),style=wx.BK_DEFAULT)
        self.panel_b=panel_balculator(nb_main,-1)
        self.panel_v=panel_version(nb_main,-1)
        nb_main.AddPage(self.panel_b,"Jitter Cal")
        nb_main.AddPage(self.panel_v,"Version")
        self.panel_b.btn_run.Bind(wx.EVT_BUTTON,self.On_Run)
        self.panel_b.chk_NSP.Bind(wx.EVT_CHECKBOX,self.Panel_Enable)
        self.panel_b.btn_collate.Bind(wx.EVT_BUTTON,self.On_Collate)

        
        
    def Panel_Enable(self,evt):      
        if self.panel_b.chk_NSP.GetValue()==0:
            self.panel_b.fbb_NSP.Disable()
            self.panel_b.btn_collate.Disable()
        elif self.panel_b.chk_NSP.GetValue()==1:
            self.panel_b.fbb_NSP.Enable()
            self.panel_b.btn_collate.Enable()
            

            
            
    def Gen_dir(self,abs_dir):
        if not(os.path.exists(str(abs_dir)+'\\pic\\')):
            os.mkdir(str(abs_dir)+'\\pic\\')

    def On_Run(self, event): 
        basic_setting=self.panel_b.get_setting()
        H0=float(basic_setting["H0"]) 
        ND=float(basic_setting["Nominal_Delay"]) 
        self.CP_filename= basic_setting["current_profile_file"]
        self.PDN_filename= basic_setting["PDN_file"]
        abs_dir=str(os.path.dirname(str(self.CP_filename)))
        if (self.CP_filename.strip()=='' or self.PDN_filename.strip()==''):
            print ("Please select the Current Profile and PDN file.")
            return()
        self.Gen_dir(abs_dir)
        (freq,i_wave_fd,fft_size,i_time)=C_PSIJ.Current_Profile(self.CP_filename,plt_dic,abs_dir)
        pdn=C_PSIJ.PDN_data(freq,self.PDN_filename,plt_dic,abs_dir)
        Voltage_FD=C_PSIJ.Calc_V_FD(freq,i_wave_fd,pdn,plt_dic,abs_dir)
        Hf=C_PSIJ.Noise_Sen_Profile(freq,plt_dic,H0,ND,abs_dir)
        C_PSIJ.Calc_PSIJ(freq,Voltage_FD,Hf,fft_size,i_time,plt_dic,abs_dir)
        
       
        print ('\n\n\t***Simulation Done.***')
        return()        

        
    def On_Collate(self, event): 
        basic_setting=self.panel_b.get_setting()
        H0=float(basic_setting["H0"]) 
        ND=float(basic_setting["Nominal_Delay"]) 
        self.NSP_filename= basic_setting["NSP_file"]
        abs_dir=str(os.path.dirname(str(self.NSP_filename)))+'\\'
        self.Gen_dir(abs_dir)
        C_PSIJ.Collate_Sen_Profile(self.NSP_filename,plt_dic,H0,ND,abs_dir)
    
        print ('\n\n\t***Collate Done.***')
        return()     
    
class panel_balculator(wx.Panel):
    def __init__(self,*args,**kwargs):
        wx.Panel.__init__(self,*args,**kwargs)
        self.sizer=wx.GridBagSizer(hgap=10,vgap=5)    
        self.sizer.Add(wx.StaticText(self,-1,r'Power Supply Include Jitter Calculator'),pos=(0,0),flag=wx.ALIGN_CENTER_VERTICAL)
        
        self.fbb_CF=filebrowse.FileBrowseButton(self,-1,size=(500,-1),labelText="Current File(time/current)",toolTip='hspice csv file')    
        self.sizer.Add(self.fbb_CF,pos=(1,0),span=(1,4)) 
        
        self.fbb_PDN=filebrowse.FileBrowseButton(self,-1,size=(500,-1),labelText="PDN curve File(freq/mag/phase)",toolTip='hspice csv file')    
        self.sizer.Add(self.fbb_PDN,pos=(2,0),span=(1,4))   
        
        self.box_ref_csv_import = wx.StaticBox(self,-1,"Jitter Sensitivity Curve")
        self.boxSizer_csvtable = wx.StaticBoxSizer(self.box_ref_csv_import,wx.VERTICAL)        
        self.sizer_csvtable=wx.GridBagSizer(hgap=10,vgap=5)

        
        self.sizer_csvtable.Add(wx.StaticText(self,-1,'H0'),pos=(0,0),flag=wx.ALIGN_CENTER_VERTICAL)
        self.txt_H0=wx.TextCtrl(self,-1,"0.24",size=(100,-1)) 
        self.sizer_csvtable.Add(self.txt_H0,pos=(0,1),span=(1,1),flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        self.sizer_csvtable.Add(wx.StaticText(self,-1,'Nominal_Delay'),pos=(1,0),flag=wx.ALIGN_CENTER_VERTICAL)
        self.txt_ND=wx.TextCtrl(self,-1,"0.246e-9",size=(100,-1)) 
        self.sizer_csvtable.Add(self.txt_ND,pos=(1,1),span=(1,1),flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        self.chk_NSP = wx.CheckBox(self,-1,'Noise Sensitivity Profile(freq/ps-per-mv)')
        self.chk_NSP.SetValue(False)
        self.sizer_csvtable.Add(self.chk_NSP,pos=(2,0),span=(1,1),flag=wx.ALIGN_CENTER_VERTICAL)
        self.fbb_NSP=filebrowse.FileBrowseButton(self,-1,size=(240,-1),labelText="",toolTip='.csv file')    
        self.fbb_NSP.Disable()
        self.sizer_csvtable.Add(self.fbb_NSP,pos=(2,1),span=(1,3)) 
        self.sizer_csvtable.Add(wx.StaticText(self,-1,r'*Check to Collate functional curve with hspice result.'),pos=(3,0),span=(1,1),flag=wx.ALIGN_CENTER_VERTICAL)
        self.btn_collate = wx.Button(self, 20, "Collate", (20, 100)) 
        self.btn_collate.SetToolTip("Collate...")
        self.btn_collate.Disable()
        self.sizer_csvtable.Add(self.btn_collate,pos=(3,1),span=(1,1),flag=wx.ALIGN_CENTER_VERTICAL) 
        self.boxSizer_csvtable.Add(self.sizer_csvtable)
        self.sizer.Add(self.boxSizer_csvtable,pos=(3,0),span=(1,4),flag=wx.ALIGN_CENTER_VERTICAL) 
        

        self.btn_run = wx.Button(self, 20, "Calculate PSIJ", (20, 100)) 
        self.btn_run.SetToolTip("Run Analysis...")
        self.sizer.Add(self.btn_run,pos=(5,1),span=(1,1),flag=wx.ALIGN_CENTER_VERTICAL) 

 
        self.SetSizer(self.sizer)    
        self.sizer.Add(wx.StaticText(self,-1,'Reference:\n\
            [1] Dan.Oh , "Analyzing On-Chip Supply Noise Induced Jitter Impact."in DesignCon 2014.\n\
            [2] Dan.Oh , "A Novel Approach to Model Dynamic Noise in Static Timing Analysis."in DesignCon 2015.')
            ,pos=(6,0),span=(1,4))
        #self.sizer.Add(wx.StaticText(self,-1,r'Link:         https://www.jitterlabs.com/support/calculators/rms-eye-closure-calculator'),pos=(9,0),span=(1,4))

    def get_setting(self):
        res={}
        res["current_profile_file"]=self.fbb_CF.GetValue()
        res["PDN_file"]=self.fbb_PDN.GetValue()
        res["NSP_file"]=self.fbb_NSP.GetValue()
        res["H0"]=self.txt_H0.GetValue()
        res["Nominal_Delay"]=self.txt_ND.GetValue()
        return res


        
class panel_version(wx.Panel):
    def __init__(self,*args,**kwargs):
        wx.Panel.__init__(self,*args,**kwargs)        
        self.sizer=wx.GridBagSizer(hgap=10,vgap=5)  
        self.sizer.Add(wx.StaticText(self,-1,'version v'+revVersion+':Initial Release'),pos=(0,0))
        self.sizer.Add(wx.StaticText(self,-1,'yanbin_c@hotmail.com'),pos=(1,0))
        self.SetSizer(self.sizer)    
        self.sizer.Fit(self)    
        self.Fit 

if __name__ == "__main__":
    app = wx.App()
    frame=MyFrame()
    frame.Show()
    app.MainLoop()


