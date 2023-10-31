import os, time, json, xlsxwriter
from tqdm import tqdm

class generate_tracker:    
    def __init__(self):
        self.proxy = '//proxy-us.intel.com:911'
        self.sysman = '/usr/bin/python3 -m Sysman.sysman '
        self.workbook = xlsxwriter.Workbook('tracker.xlsx')
        self.worksheet = self.workbook.add_worksheet()
        self.host = os.popen('hostname').read().replace('\n','')
        self.gdc = 'login01.lab10b2.deacluster.intel.com'
        self.admin_flex = 'a001admin001'
        self.debug_flex = 'a001ivedebug001.fl30lcent1.deacluster.intel.com'
        
        
    def get_user_data(self):

        self.logname = os.popen('env | grep LOGNAME').read().replace('\n','')
        self.logname = self.logname.split('=')
        self.user = self.logname[1]
        with open('jira.txt','r') as jira_id:
            self.ticket = jira_id.read()
            self.ticket = self.ticket.replace('\n','').replace(' ','')
        with open('bkc.txt','r') as bkcChecker:
            self.bkcChecker = bkcChecker.read()
            self.bkcChecker = self.bkcChecker.replace('\n','').replace(' ','')
        os.popen('rm jira.txt')
        os.popen('rm bkc.txt')
        return self.user, self.ticket, self.bkcChecker
    
    def get_nodes(self,ticket):
        #ticket = 'sjlealru'
        if self.host == self.gdc:
            print('Server GDC')
            self.nodes = os.popen(f'{self.sysman} -P {str(ticket)} --print-names').read()
        elif self.host == self.admin_flex:
            print('Server Flex')
            self.nodes = os.popen(f'ssh {self.debug_flex}  {self.sysman} -P {str(ticket)} --print-names').read()
        self.nodes = self.nodes.replace('\n','').split(' ')
        self.nodes = sorted(self.nodes)
        print(len(self.nodes))
        if len(self.nodes) == 1:
            print('Wrong pool name...')
            quit()
        return self.nodes
        
    def add_nodes_to_known_hosts(self,user,nodes):      
        self.ssh_test = {}
        self.pwd = os.popen('pwd').read().replace('\n','')
        #print(self.pwd)
        for i in tqdm(range(0,len(nodes)), desc=(f'Checking SSH in {len(nodes)} nodes'), leave=False):
        #for node in nodes:
            os.chdir(f'/home/{user}/.ssh/')
            os.popen(f"sed -i /'{str(nodes[i])}'/d known_hosts")
            os.chdir(self.pwd)
            with open('ssh_test.sh','w') as sh_file:
                sh_file.write(f'ssh -o ConnectTimeout=5 -q {str(nodes[i])} exit\n')
                sh_file.write('echo $? > ssh_result.txt')
            #os.system('cat ssh_test.sh')
            os.popen('chmod 777 ssh_test.sh')
            os.system('./ssh_test.sh')
            #for i in tqdm(range(0,len(nodes)), desc=(f'Getting nodes info ET {str(self.timer)}')):
            time.sleep(1)
            #os.system('cat ssh_result.txt')             
            with open('ssh_result.txt','r') as ssh_result:
                self.ssh_result = ssh_result.readline()
                #print('\n'+self.ssh_result)
                self.ssh_result = self.ssh_result.replace('\n','')
            os.popen('rm ssh_result.txt') 
            #print(f'es {str(self.ssh_result)}')
            if self.ssh_result == '0':
                self.ssh_test[nodes[i]] = True
            else:
                self.ssh_test[nodes[i]] = False
            #print(f'El node es {node} y su estado es {sed}.')
            #time.sleep(2)
        return self.ssh_test
               
    def get_checker(self,user,bkcChecker):
        #checker = 'GDC_EGS_PLR4'
        #checker = 'GDC_EMR_BKC13'
        self.checker_data = os.chdir(f'/home/{user}/openstack-scripts/verification_tools/bkc_checker/')
        self.checker_data = os.popen(f'python bkcManager.py -b {bkcChecker} -s').read()
        if len(self.checker_data) == 0:
            print('Wrong BKC checker...')
            quit()
        self.checker_data = self.checker_data.split('\n')
        if len(self.checker_data) == 34:
            osImage = self.checker_data[23]
            osImage = osImage.split(' - ')
            osImage_ = osImage[0]
            self.checker_data[23] = osImage_
        self.checker_data = '","'.join(self.checker_data)
        self.checker_data = '"'+self.checker_data[:-2].replace(':','":"').replace(' ','')
        self.checker_data = '{'+self.checker_data+'}'
        self.checker_data = json.loads(self.checker_data)
        try:
            self.checker_data['osImageVersion'] = self.checker_data['osImageVersion']+' - '+osImage[1]
        except:
            pass
        print(self.checker_data)
        return self.checker_data
                
    def create_template(self):
        self.set_path = os.chdir(self.pwd)
        format = self.workbook.add_format()
        format.set_bold(True)
        print(type(self.checker_data))
        try:
            self.header = ['Node ID','System in Maintenance Pool','SSH connection','Is the blue indicator LED ON?','ClearCMOS','Mem Config','Jumpers verified','get_straps','CPLD Main ','CPLD SECONDARY','Spr installed & Geometry enabled','BIOS: '+self.checker_data['bmcBiosVersion'],'uCode: '+self.checker_data['osUcode'],'BMC: '+self.checker_data['bmcVersion'],'System Booting?','BIOS knobs configured?','CFR update force','FPRR Bios knob disabled?','Columbiaville '+self.checker_data['osCLV1FwVersion'],'Columbiaville '+self.checker_data['osCLV1FwVersion'],'Remove M.2','Arbordale 2CV10026','Fortville v8.10','Boot order?','OS IMAGE '+self.checker_data['osImageVersion'],'Boot override','Post_instal.sh?','Inventory Script?','Check Correct Mem Size?','VR FW Verified and Deploy Tracker updated?','BKCChecker?','is the blue indicator LED OFF?','Target Pool?','Username','Comments']
        except:
            self.header = ['Node ID','System in Maintenance Pool','SSH connection','Is the blue indicator LED ON?','ClearCMOS','Mem Config','Jumpers verified','get_straps','CPLD Main ','CPLD SECONDARY','Spr installed & Geometry enabled','BIOS: '+self.checker_data['bmcBiosVersion'],'uCode: '+self.checker_data['osUcode'],'BMC: '+self.checker_data['bmcVersion'],'System Booting?','BIOS knobs configured?','CFR update force','FPRR Bios knob disabled?','Columbiaville '+self.checker_data['osCLV1FwVersion'],'Columbiaville '+self.checker_data['osCLV1FwVersion'],'Remove M.2','Arbordale 2CV10026','Fortville v8.10','Boot order?','OS IMAGE '+self.checker_data['osKernelVersion'],'Boot override','Post_instal.sh?','Inventory Script?','Check Correct Mem Size?','VR FW Verified and Deploy Tracker updated?','BKCChecker?','is the blue indicator LED OFF?','Target Pool?','Username','Comments']
        for column, field in enumerate (self.header):
            self.worksheet.write(0, column, field, format)
        self.worksheet.set_column(0,0,15)
        #return self.workbook, self.xlsx
        
    def get_info(self,nodes,user,ssh_test):
        os.chdir('/home/'+user+'/openstack-scripts/verification_tools/')
        #os.system('pwd')
        self.timer = 0
        #os.system('cat node')
        try:
            os.system('rm node_list.txt')
        except:
            pass
        #print(len(nodes))
        #print(nodes)
        for node in nodes:
            if self.ssh_test[node] == True:
                self.timer = self.timer + 9
                with open('node_list.txt','a') as node_list:
                    #print('creando archivo '+ node)
                    node_list.write(f'{node}\n')
                    #os.system('ls | grep node_list')
                    #print(f'{node}')
            else:
                pass
                print('No ssh')
        #os.system('cat node_list.txt')        
        self.info = os.system('./list_get_info.sh node_list.txt > list_info.csv')
        #print(self.timer)
        
        for i in tqdm(range(0,len(nodes)), desc=(f'Getting nodes info ET {str(self.timer)}'), leave=False):
            time.sleep(9)
            
            
            
        self.info = os.popen('cat list_info.csv').read()
        self.info = self.info.split('\n')
        #print(self.info)
        del self.info[-1]
        #print(self.info)
        #print(len(self.info))
        
        self.nodes_info = {}
        for index, data in enumerate (self.info):
            self.info[index] = self.info[index].split(',')             
        for index, data in enumerate (self.info):
            if index == 0:
                self.get_info_header = data
                #print(self.get_info_header)
            else:
                #print(data)
                data_dict = {f'{data[1]}':{}}
                for d, g in zip(data, self.get_info_header):
                    data_dict[f'{data[1]}'][g] = d                
                self.nodes_info.update(data_dict)
                #data_dict[f'{data[1]}']
        #print(self.nodes_info)
        return self.nodes_info, self.timer
        #return self.info
    
    def compare_info(self):
        DIMM = 'Synchronous Registered (Buffered)'
        CPS = 'Non-Volatile LRDIMM'
        self.set_path = os.chdir(self.pwd)
        header_format = self.workbook.add_format({'text_wrap': True, 'bold':True, 'border':1, 'font_size':10, 'align':'center', 'valign':'vcenter'})
        text_format = self.workbook.add_format({'border':1, 'font_size':10, 'align':'center', 'valign':'vcenter'})
        try:
            self.header = ['Node ID','System in Maintenance Pool','SSH connection','Is the blue indicator LED ON?','ClearCMOS','Mem Config','Jumpers verified','get_straps','CPLD Main ','CPLD SECONDARY','Spr installed & Geometry enabled','BIOS: '+self.checker_data['bmcBiosVersion'],'uCode: '+self.checker_data['osUcode'],'BMC: '+self.checker_data['bmcVersion'],'System Booting?','BIOS knobs configured?','CFR update force','FPRR Bios knob disabled?','Columbiaville '+self.checker_data['osCLV1FwVersion'],'Columbiaville '+self.checker_data['osCLV1FwVersion'],'Remove M.2','Arbordale 2CV10026','Fortville v8.10','Boot order?','OS IMAGE '+self.checker_data['osImageVersion'],'Boot override','Post_instal.sh?','Inventory Script?','Check Correct Mem Size?','VR FW Verified and Deploy Tracker updated?','BKCChecker?','is the blue indicator LED OFF?','Target Pool?','Username','Comments']
        except:
            self.header = ['Node ID','System in Maintenance Pool','SSH connection','Is the blue indicator LED ON?','ClearCMOS','Mem Config','Jumpers verified','get_straps','CPLD Main ','CPLD SECONDARY','Spr installed & Geometry enabled','BIOS: '+self.checker_data['bmcBiosVersion'],'uCode: '+self.checker_data['osUcode'],'BMC: '+self.checker_data['bmcVersion'],'System Booting?','BIOS knobs configured?','CFR update force','FPRR Bios knob disabled?','Columbiaville '+self.checker_data['osCLV1FwVersion'],'Columbiaville '+self.checker_data['osCLV1FwVersion'],'Remove M.2','Arbordale 2CV10026','Fortville v8.10','Boot order?','OS IMAGE '+self.checker_data['osKernelVersion'],'Boot override','Post_instal.sh?','Inventory Script?','Check Correct Mem Size?','VR FW Verified and Deploy Tracker updated?','BKCChecker?','is the blue indicator LED OFF?','Target Pool?','Username','Comments']
        
        for column, field in enumerate (self.header):
            self.worksheet.write(0, column, field, header_format)
        self.worksheet.set_column(0,0,15)
        cellFormat = self.workbook.add_format({'border': 1})
        columns = len(self.nodes_info)
        
        
        #for i in tqdm(range(0,len(nodes)), desc=(f'Checking SSH in {len(nodes)} nodes'), leave=False):
        for row, current_node in enumerate (self.ssh_test):
            for column in range(0,35):
                self.worksheet.write(row+1, column, None, cellFormat)
            #if self.ssh_test[current_node] == 'zp3110b001s1411':
            #    break
            if self.ssh_test[current_node] == True:
                self.worksheet.write(row+1, 0, current_node, text_format)
                self.worksheet.write(row+1, 1, 'Yes', text_format)
                self.worksheet.write(row+1, 2, 'Yes', text_format)
                self.worksheet.write(row+1, 33, self.user, text_format)
                
                try:
                    dimm_count = os.popen(f'ssh {current_node} dmidecode -t memory | grep "{DIMM}" -c').read()
                    dimm_count = dimm_count.replace('\n','')
                    if dimm_count == '32':
                        cps_count = os.popen(f'ssh {current_node} dmidecode -t memory | grep "{CPS}" -c').read()
                        cps_count = cps_count.replace('\n','')
                        if cps_count != '0':                          
                            self.worksheet.write(row+1, 5, '2DPC+'+cps_count+'CPS', text_format)
                        else:
                            self.worksheet.write(row+1, 5, '2DPC', text_format)
                    elif dimm_count == '16':
                        time.sleep(0.5)
                        cps_count = os.popen(f'ssh {current_node} dmidecode -t memory | grep "{CPS}" -c').read()
                        cps_count = cps_count.replace('\n','')
                        print(cps_count)
                        print(type(cps_count))
                        time.sleep(0.5)
                        if cps_count != '0':                          
                            self.worksheet.write(row+1, 5, '1DPC+'+cps_count+'CPS', text_format)
                            #print('opt 1')
                        else:
                            self.worksheet.write(row+1, 5, '1DPC', text_format)
                            #print('opt 2')
                    else:
                         self.worksheet.write(row+1, 5, dimm_count+' DIMMs', text_format)
                except:
                    pass
                '''
                try:
                    if self.checker_data['bmcDimmCount'] == 32:
                    
                except:
                '''    
                
                try:
                    if self.checker_data['bmcVersion'] == self.nodes_info[current_node]['bmcVersion']:
                        self.worksheet.write(row+1, 13, 'Done', text_format)
                    else:
                        self.worksheet.write(row+1, 13, self.nodes_info[current_node]['bmcVersion'], text_format)                                        
                except:
                    print(f'{current_node} BMC')
                try:
                    if self.checker_data['bmcBiosVersion'] == self.nodes_info[current_node]['bmcBiosVersion']:
                        self.worksheet.write(row+1, 11, 'Done', text_format)
                    else:
                        self.worksheet.write(row+1, 11, 'Fail', text_format)
                except:
                    print(f'{current_node} BIOS')
                try:
                    if self.checker_data['bmcCpldVersion'] == self.nodes_info[current_node]['bmcCpldVersion']:
                        self.worksheet.write(row+1, 8, 'Done', text_format)
                        self.worksheet.write(row+1, 9, 'Done', text_format)
                    else:
                        self.worksheet.write(row+1, 8, 'Fail', text_format)
                        self.worksheet.write(row+1, 9, 'Fail', text_format)
                except:
                    print(f'{current_node} CPLD')
                try:    
                    if self.checker_data['osUcode'] == self.nodes_info[current_node]['osUcode']:
                        self.worksheet.write(row+1, 12, 'Done', text_format)
                    else:
                        self.worksheet.write(row+1, 12, self.nodes_info[current_node]['osUcode'], text_format)
                except:
                    print(f'{current_node} UCODE')
                
                try:
                    if self.checker_data['osImageVersion'] == self.nodes_info[current_node]['osImageVersion']:
                        self.worksheet.write(row+1, 23, 'Done', text_format)
                        self.worksheet.write(row+1, 24, 'Done', text_format)
                        self.worksheet.write(row+1, 25, 'Done', text_format)
                        self.worksheet.write(row+1, 26, 'Done', text_format)
                    else:
                        self.worksheet.write(row+1, 24, 'Fail', text_format)
                except:
                    
                    if self.checker_data['osKernelVersion'] == self.nodes_info[current_node]['osKernelVersion']:
                        self.worksheet.write(row+1, 23, 'Done', text_format)
                        self.worksheet.write(row+1, 24, 'Done', text_format)
                        self.worksheet.write(row+1, 25, 'Done', text_format)
                        self.worksheet.write(row+1, 26, 'Done', text_format)
                    else:
                        self.worksheet.write(row+1, 24, 'Fail', text_format)
                          
                if self.checker_data['osCLV1FwVersion'] == self.nodes_info[current_node]['osCLV1FwVersion']:
                    self.worksheet.write(row+1, 18, 'Done', text_format)
                else:
                    self.worksheet.write(row+1, 18, self.nodes_info[current_node]['osCLV1FwVersion'], text_format)
                
                if self.checker_data['osCLV2FwVersion'] == self.nodes_info[current_node]['osCLV2FwVersion']:
                    self.worksheet.write(row+1, 19, 'Done', text_format)
                else:
                    self.worksheet.write(row+1, 19, self.nodes_info[current_node]['osCLV2FwVersion'], text_format)
                
                if self.checker_data['osFTVFwVersion'] == self.nodes_info[current_node]['osFTVFwVersion']:
                    self.worksheet.write(row+1, 22, 'Done', text_format)
                else:
                    self.worksheet.write(row+1, 22, self.nodes_info[current_node]['osFTVFwVersion'], text_format)
                if self.checker_data['osArbFwVersion'] == self.nodes_info[current_node]['osArbFwVersion']:
                    self.worksheet.write(row+1, 21, 'Done', text_format)
                else:
                    self.worksheet.write(row+1, 21, 'Fail', text_format)    
            else:
                self.worksheet.write(row+1, 0, current_node, text_format)
                self.worksheet.write(row+1, 1, 'Yes', text_format)
                self.worksheet.write(row+1, 2, 'Fail', text_format)
                self.worksheet.write(row+1, 33, self.user, text_format)
                
        pass_style = self.workbook.add_format({'bg_color': 'c6efce','border':1})
        fail_style = self.workbook.add_format({'bg_color': 'ffc7ce','border':1})
        wip_style = self.workbook.add_format({'bg_color': 'ffeb9c','border':1})
        border_format = self.workbook.add_format({'border':1})    
        row+=2
        
        self.worksheet.conditional_format(f'A1:AH{row}', {'type': 'text',
                                                          'criteria': 'containing',
                                                          'value': 'Done',
                                                          'format': pass_style})
        
        self.worksheet.conditional_format(f'A1:AH{row}', {'type': 'text',
                                                          'criteria': 'containing',
                                                          'value': 'Yes',
                                                          'format': pass_style})
        
        self.worksheet.conditional_format(f'A1:AH{row}', {'type': 'text',
                                                          'criteria': 'containing',
                                                          'value': 'System OK',
                                                          'format': pass_style})
        
        self.worksheet.conditional_format(f'A1:AH{row}', {'type': 'text',
                                                          'criteria': 'containing',
                                                          'value': 'Fail',
                                                          'format': fail_style})
        
        self.worksheet.conditional_format(f'A1:AH{row}', {'type': 'text',
                                                          'criteria': 'containing',
                                                          'value': 'No',
                                                          'format': fail_style})
        
        self.worksheet.conditional_format(f'A1:AH{row}', {'type': 'text',
                                                          'criteria': 'containing',
                                                          'value': 'WIP',
                                                          'format': wip_style})
        
        self.workbook.close()
                                   

def main():
    tracker = generate_tracker()
    
    
    User, Pool, BkcChecker = tracker.get_user_data()
    Nodes = tracker.get_nodes(Pool)
    BKC_Checker = tracker.get_checker(User,BkcChecker)

    SSH_Status = tracker.add_nodes_to_known_hosts(User,Nodes)
    print(SSH_Status)
    #BKC_Checker = tracker.get_checker(User,BkcChecker)

    Get_node_info = tracker.get_info(Nodes,User,SSH_Status)
    Compare = tracker.compare_info()
    
if __name__ == "__main__":
    main() 