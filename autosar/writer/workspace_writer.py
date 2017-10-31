from autosar.writer.writer_base import BaseWriter
from autosar.writer.package_writer import PackageWriter
from autosar.base import filter_packages
import collections

class WorkspaceWriter(BaseWriter):
   def __init__(self, version, patch, packageWriter):
      super().__init__(version, patch)
      assert(isinstance(packageWriter, PackageWriter))
      self.packageWriter=packageWriter
   
   def saveXML(self, ws, fp, packages, ignore):
      fp.write(self.toXML(ws, packages, ignore))

   def toXML(self, ws, filters, ignore):
      lines=self.beginFile()
      result='\n'.join(lines)+'\n'
      filtered_packages = filter_packages(ws.packages, filters)
      for package in filtered_packages:
         lines=self.packageWriter.toXML(package, filters, ignore)
         if len(lines)>0:
            lines=self.indent(lines,2)
            result+='\n'.join(lines)+'\n'
      lines=self.endFile()
      return result+'\n'.join(lines)+'\n'
   
   def toCode(self, ws, packages=None, ignore=None, head=None, tail=None, module=False, indent=3):
      localvars = collections.OrderedDict()
      localvars['ws']=ws
      indentStr=indent*' '
      if module == False:
         #head
         if head is None:
            lines=['import autosar', 'ws=autosar.workspace()']
            result='\n'.join(lines)+'\n\n'
         else:            
            if isinstance(head,list):
               head = '\n'.join(head)
            assert(isinstance(head,str))
            result = head+'\n\n'      
         
         
         #body
         for package in ws.packages:
            if (isinstance(packages, collections.Iterable) and package.name in packages) or (isinstance(packages, str) and package.name==packages) or (packages is None):
               lines=self.packageWriter.toCode(package, ignore, localvars)
               if len(lines)>0:
                  result+='\n'.join(lines)+'\n'
         #tail
         if tail is None:
            result+='\n'+'print(ws.toXML())\n'
         else:
            if isinstance(tail,list):
               tail = '\n'.join(tail)
            assert(isinstance(tail,str))
            result+='\n'+tail
         return result
      else:
         if head is None:
            head=[
               ['import autosar'],
               ['ws = autosar.workspace()']
            ]
         if len(head)!=2:
            raise ValueError('when module=True then head must have exactly two elements (list of lists)')
         if isinstance(head[0], collections.Iterable):
            head[0] = '\n'.join(head[0])
         assert(isinstance(head[0],str))
         result = head[0]+'\n\n'
         #body
         result+='def apply(ws):\n'
         for package in ws.packages:
            if (isinstance(packages, collections.Iterable) and package.name in packages) or (isinstance(packages, str) and package.name==packages) or (packages is None):
               lines=self.packageWriter.toCode(package, ignore, localvars)
               if len(lines)>0:
                  lines=[indentStr+x for x in lines]
                  result+='\n'.join(lines)+'\n'
         
         #tail
         result+="\nif __name__=='__main__':\n"
         if isinstance(head[1], collections.Iterable):
            head[1] = '\n'.join([indentStr+x for x in head[1]])
         else:
            head[1] = '\n'.join([indentStr+x for x in head[1].split('\n')])
         assert(isinstance(head[1],str))
         result+=head[1]+'\n'
         result+=indentStr+'apply(ws)\n'
         if tail is None:
            result+=indentStr+'print(ws.toXML())\n'
         else:
            if isinstance(tail,list):
               tail = '\n'.join([indentStr+x for x in tail])
            else:
               tail = '\n'.join([indentStr+x for x in tail.split('\n')])
            assert(isinstance(tail,str))
            result+=tail+'\n'
         return result
      

      
   def saveCode(self, ws, fp, packages=None, ignore=None, head=None, tail=None, module=False):
      fp.write(self.toCode(ws, packages, ignore, head, tail, module))