#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dendropy,logging,os,shutil,sys
import Settings as sp

class Rerooter:
    # general
    appLoger=None
    settings=None
    # tree-related
    tree=None
    outputFilename="ngsphy.tree"
    outputFilePath=""

    def __init__(self, settings):
        self.appLogger=logging.getLogger('ngsphy')
        self.appLogger.debug('Rerooting')
        self.settings=settings
        self.outputFilePath=os.path.join(\
            self.settings.outputFolderPath,\
            self.outputFilename\
        )


    def run(self):
        self.appLogger.debug('Running rerooting')
        try:
            self.tree=dendropy.Tree.get(path=self.settings.newickFilePath, schema="newick",preserve_underscores=True)
        except Exception as ex:
            return False, ex

        print(self.tree.as_ascii_plot())
        newroot = self.tree.find_node_with_taxon_label(self.settings.referenceTipLabel)
        if newroot:
            self.tree.reroot_at_edge(newroot.edge, update_bipartitions=False)
            print(self.tree.as_ascii_plot())
        else:
            return False, "{0}\n\t{1}\n\t{2}".format(\
            "Rerooting problem.",\
            "Something might be wrong with the reference label.",\
            "Please Verify. Exiting"\
            )

        leaves=[node.taxon.label for node in self.tree.leaf_node_iter() if not node.taxon.label in [self.settings.referenceTipLabel, "1_0_1"]]
        print(leaves)
        try:
            mrca=self.tree.mrca(taxon_labels=leaves)
            self.tree.prune_taxa_with_labels([self.settings.referenceTipLabel])
            print(self.tree.as_ascii_plot())
            for item in self.tree.leaf_node_iter():
                if self.tree.seed_node==item.parent_node:
                    print(item.taxon.label)
                    item.taxon.label="0_0_0"
                    print(item.taxon.label)
            print(self.tree.as_ascii_plot())
            


        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            message="Rerooter - run: {0} | {1} - File: {2} - Line:{3}".format(ex,exc_type, fname, exc_tb.tb_lineno)
            return False, message
        return True,""

    def generateFolderStructure(self):
        folder=os.path.join(self.settings.path,self.settings.projectName,"1")
        try:
            os.makedirs(folder)
            self.appLogger.info("Generating project folder ({0})".format(folder))
        except:
            self.appLogger.debug("Project folder exists ({0})".format(folder))
        try:
            shutil.copyfile(self.settings.referenceSequenceFilePath, os.path.joing(folder, "reference.fasta"))
        except:
            self.appLogger.debug("File already exists in this location ({0})".format(os.path.joing(folder, "reference.fasta")))

    def writeTree(self):
        self.tree.write(\
            path=self.outputFilePath,\
            schema="newick",\
            suppress_rooting=True\
            )