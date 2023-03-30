"""
This module implements functions to deal with variables
"""

from . import copy_doc, tostring, alltext

def getVarList(doc):
    """
    :param doc: etree to use
    :return: a dict of dictionaries. Each key of the primary dictionnary is the
             variable name. The associated dictionnary has the following keys:
              - as: list of array specifications
              - asx: same
              - n: name of the variable as written
              - i: intent
              - t: type specification
              - arg: True if variable is a dummy argument
    """
    def decode_array_specs(array_specs):
        as_list = []
        asx_list = []
        for array_spec in array_specs:
            lb = array_spec.find('.//{*}lower-bound')
            ub = array_spec.find('.//{*}upper-bound')
            as_list.append([alltext(lb) if lb is not None else None, alltext(ub) if ub is not None else None])
            asx_list.append([tostring(lb) if lb is not None else None, tostring(ub) if ub is not None else None])
        return as_list, asx_list
        
    #Find dummy arguments
    dummy_args = [e.text for e in doc.findall('.//{*}dummy-arg-LT/{*}arg-N/{*}N/{*}n')]

    decl_dict = {}
    decl_stmts = doc.findall('.//{*}T-decl-stmt')
    #Loop on each declaration statement
    for decl_stmt in decl_stmts:
        t_spec = alltext(decl_stmt.find('.//{*}_T-spec_'))
        i_spec = decl_stmt.find('.//{*}intent-spec')
        if i_spec is not None: i_spec = i_spec.text

        #Dimensions declared with the DIMENSION attribute
        array_specs =decl_stmt.findall('.//{*}attribute//{*}array-spec//{*}shape-spec')
        as0_list, asx0_list = decode_array_specs(array_specs)
        
        #Loop on each declared variables
        en_decls = decl_stmt.findall('.//{*}EN-decl')
        for en_decl in en_decls:
            n = alltext(en_decl.find('.//{*}n'))
            #Dimensions declared after the variable name
            array_specs = en_decl.findall('.//{*}array-spec//{*}shape-spec')
            as_list, asx_list = decode_array_specs(array_specs)

            decl_dict[n] = {'as0': as0_list, 'asx0': asx0_list,
                            'as': as_list, 'asx': asx_list,
                            'n': n, 'i': i_spec, 't': t_spec, 'arg': n in dummy_args}
    return decl_dict

def showVarList(doc):
    """
    Display on stdout a nive view of all the variables
    :param doc: etree to use
    """
    for v in getVarList(doc).values():
        isscalar = len(v['as0']) == len(v['as'])
        print('Variable name {}:'.format(v['n']))
        if isscalar:
            print('  is scalar')
        else:
            d = v['as'] if len(v['as0']) == 0 else v['as0']
            print('  is of rank {}, with dimensions {}'.format(len(d),
                                ', '.join([(':'.join([('' if s is None else s) for s in d[i]])) for i in range(len(d))])))
        if v['arg']:
            print('  is a dummy argument {}'.format('without intent' if v['i'] is None else 'with intent {}'.format(v['i'])))
        else:
            print('  is a local variable')
        print()

class Variables():
    @copy_doc(getVarList)
    def getVarList(self):
        return getVarList(doc=self._xml)

    @copy_doc(showVarList)
    def showVarList(self):
        return showVarList(doc=self._xml)
