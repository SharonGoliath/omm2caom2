# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2018.                            (c) 2018.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
# ***********************************************************************
#

import os

from mock import Mock, patch

from astropy.io import fits

from omm2caom2 import omm_composable, omm_footprint_augmentation
from omm2caom2 import omm_preview_augmentation, manage_composable
from caom2 import obs_reader_writer, SimpleObservation, Algorithm
from omm2caom2 import CadcException, OmmName
from cadcutils import net
import cadcdata
import caom2repo


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
TESTDATA_DIR = os.path.join(THIS_DIR, 'data')


def _init_config():
    test_config = manage_composable.Config()
    test_config.working_directory = THIS_DIR
    test_config.collection = 'OMM'
    test_config.netrc_file = os.path.join(TESTDATA_DIR, 'test_netrc')
    test_config.work_file = 'todo.txt'
    test_config.logging_level = 'DEBUG'
    return test_config


def test_meta_execute():
    test_obs_id = 'test_obs_id'
    test_dir = os.path.join(THIS_DIR, test_obs_id)

    # clean up from previous tests
    if os.path.exists(test_dir):
        for ii in os.listdir(test_dir):
            os.remove(os.path.join(test_dir, ii))
        os.rmdir(test_dir)
    netrc = os.path.join(THIS_DIR, 'test_netrc')
    assert os.path.exists(netrc)

    # mocks for this test
    data_cmd_orig = omm_composable.CaomExecute._data_cmd_info
    omm_composable.CaomExecute._data_cmd_info = Mock(side_effect=_get_fname)
    exec_cmd_orig = manage_composable.exec_cmd

    test_config = _init_config()
    try:
        # run the test
        manage_composable.exec_cmd = Mock()
        test_executor = omm_composable.Omm2Caom2Meta(test_config, test_obs_id)
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e

        # check that things worked as expected
        assert manage_composable.exec_cmd.called
        assert omm_composable.CaomExecute._data_cmd_info.called
    finally:
        omm_composable.CaomExecute._data_cmd_info = data_cmd_orig
        manage_composable.exec_cmd = exec_cmd_orig


def test_meta_local_execute():
    test_obs_id = 'test_obs_id'
    test_output_fname = os.path.join(TESTDATA_DIR,
                                     OmmName(test_obs_id).get_model_file_name())

    # clean up from previous tests
    if os.path.exists(test_output_fname):
        os.remove(test_output_fname)
    netrc = os.path.join(TESTDATA_DIR, 'test_netrc')
    assert os.path.exists(netrc)
    exec_cmd_orig = manage_composable.exec_cmd
    manage_composable.exec_cmd = Mock()

    test_config = _init_config()
    test_config.working_directory = TESTDATA_DIR
    test_config.logging_level = 'INFO'

    # run the test
    try:
        try:
            test_executor = omm_composable.Omm2Caom2LocalMeta(
                test_config, test_obs_id, OmmName(test_obs_id).get_file_name())
            test_executor.execute(None)
        except CadcException as e:
            assert False, e
        assert manage_composable.exec_cmd.called
    finally:
        manage_composable.exec_cmd = exec_cmd_orig


def test_data_execute():
    test_obs_id = 'TEST_OBS_ID'
    test_dir = os.path.join(THIS_DIR, test_obs_id)
    test_fits_fqn = os.path.join(test_dir,
                                 OmmName(test_obs_id).get_file_name())
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)
    precondition = open(test_fits_fqn, 'w')
    precondition.close()

    footprint_orig = omm_footprint_augmentation.visit
    omm_footprint_augmentation.visit = Mock()
    preview_orig = omm_preview_augmentation.visit
    omm_preview_augmentation.visit = Mock()
    read_orig = obs_reader_writer.ObservationReader.read
    obs_reader_writer.ObservationReader.read = Mock(side_effect=_read_obs)
    data_cmd_orig = omm_composable.CaomExecute._data_cmd_info
    os_path_exists_orig = os.path.exists
    os.path.exists = Mock(return_value=True)
    exec_cmd_orig = manage_composable.exec_cmd
    manage_composable.exec_cmd = Mock()
    put_orig = omm_composable.CaomExecute._data_cmd_put
    omm_composable.CaomExecute._data_cmd_put = Mock()
    checksum_orig = omm_composable.CaomExecute._compare_checksums
    omm_composable.CaomExecute._compare_checksums = Mock()
    test_config = _init_config()

    try:
        omm_composable.CaomExecute._data_cmd_info = Mock(side_effect=_get_fname)

        # run the test
        test_executor = omm_composable.Omm2Caom2Data(test_config, test_obs_id)
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e

        # check that things worked as expected
        assert manage_composable.exec_cmd.called
        assert omm_footprint_augmentation.visit.called
        assert omm_preview_augmentation.visit.called
        assert omm_composable.CaomExecute._data_cmd_put.called
        assert omm_composable.CaomExecute._compare_checksums.called
    finally:
        obs_reader_writer.ObservationReader.read = read_orig
        omm_footprint_augmentation.visit = footprint_orig
        omm_preview_augmentation.visit = preview_orig
        omm_composable.CaomExecute._data_cmd_info = data_cmd_orig
        os.path.exists = os_path_exists_orig
        manage_composable.exec_cmd = exec_cmd_orig
        omm_composable.CaomExecute._data_cmd_put = put_orig
        omm_composable.CaomExecute._compare_checksums = checksum_orig


def test_data_local_execute():
    test_obs_id = 'test_obs_id'

    fp_visit_orig = omm_footprint_augmentation.visit
    prev_visit_orig = omm_preview_augmentation.visit
    read_orig = obs_reader_writer.ObservationReader.read
    exec_cmd_orig = manage_composable.exec_cmd
    manage_composable.exec_cmd = Mock()
    put_orig = omm_composable.CaomExecute._data_cmd_put
    omm_composable.CaomExecute._data_cmd_put = Mock()
    checksum_orig = omm_composable.CaomExecute._compare_checksums
    omm_composable.CaomExecute._compare_checksums = Mock()

    try:
        omm_footprint_augmentation.visit = Mock()
        omm_preview_augmentation.visit = Mock()
        obs_reader_writer.ObservationReader.read = Mock(side_effect=_read_obs)

        test_config = _init_config()
        # run the test
        test_executor = omm_composable.Omm2Caom2LocalData(
            test_config, test_obs_id,
            OmmName(test_obs_id).get_compressed_file_name())
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e

        # check that things worked as expected - no cleanup
        assert manage_composable.exec_cmd.called
        assert omm_footprint_augmentation.visit.called
        assert omm_preview_augmentation.visit.called
        assert omm_composable.CaomExecute._data_cmd_put.called
        assert omm_composable.CaomExecute._compare_checksums.called
    finally:
        obs_reader_writer.ObservationReader.read = read_orig
        omm_footprint_augmentation.visit = fp_visit_orig
        omm_preview_augmentation.visit = prev_visit_orig
        manage_composable.exec_cmd = exec_cmd_orig
        omm_composable.CaomExecute._data_cmd_put = put_orig
        omm_composable.CaomExecute._compare_checksums = checksum_orig


def test_data_store():
    test_obs_id = 'test_obs_id'
    test_config = _init_config()
    exec_cmd_orig = manage_composable.exec_cmd
    manage_composable.exec_cmd = Mock()

    try:

        # run the test
        test_executor = omm_composable.Omm2Caom2Store(
            test_config, test_obs_id,
            OmmName(test_obs_id).get_compressed_file_name())
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e
        assert manage_composable.exec_cmd.called

    finally:
        manage_composable.exec_cmd = exec_cmd_orig


def test_scrape():
    test_obs_id = 'test_obs_id'
    test_output_fname = os.path.join(TESTDATA_DIR,
                                     OmmName(test_obs_id).get_model_file_name())

    # clean up from previous tests
    if os.path.exists(test_output_fname):
        os.remove(test_output_fname)
    netrc = os.path.join(TESTDATA_DIR, 'test_netrc')
    assert os.path.exists(netrc)

    test_config = _init_config()
    test_config.working_directory = TESTDATA_DIR
    test_config.logging_level = 'INFO'
    exec_cmd_orig = manage_composable.exec_cmd
    manage_composable.exec_cmd = Mock()

    try:
        test_executor = omm_composable.Omm2Caom2Scrape(
            test_config, test_obs_id,
            OmmName(test_obs_id).get_compressed_file_name())
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e
        assert manage_composable.exec_cmd.called

    finally:
        manage_composable.exec_cmd = exec_cmd_orig


def test_data_scrape_execute():
    test_obs_id = 'test_obs_id'

    fp_visit_orig = omm_footprint_augmentation.visit
    prev_visit_orig = omm_preview_augmentation.visit
    read_orig = obs_reader_writer.ObservationReader.read
    try:
        omm_footprint_augmentation.visit = Mock()
        omm_preview_augmentation.visit = Mock()
        obs_reader_writer.ObservationReader.read = Mock(side_effect=_read_obs)

        test_config = _init_config()

        # run the test
        test_executor = omm_composable.Omm2Caom2DataScrape(
            test_config, test_obs_id,
            OmmName(test_obs_id).get_compressed_file_name())
        try:
            test_executor.execute(None)
        except CadcException as e:
            assert False, e

        # check that things worked as expected
        assert omm_footprint_augmentation.visit.called
        assert omm_preview_augmentation.visit.called
    finally:
        obs_reader_writer.ObservationReader.read = read_orig
        omm_footprint_augmentation.visit = fp_visit_orig
        omm_preview_augmentation.visit = prev_visit_orig


def test_organize_executes():
    test_obs_id = 'Ctest_obs_id_SCI'
    test_config = _init_config()
    test_config.use_local_files = True
    log_file_directory = os.path.join(THIS_DIR, 'logs')
    test_config.log_file_directory = log_file_directory
    success_log_file_name = 'success_log.txt'
    test_config.success_log_file_name = success_log_file_name
    failure_log_file_name = 'failure_log.txt'
    test_config.failure_log_file_name = failure_log_file_name
    retry_file_name = 'retries.txt'
    test_config.retry_file_name = retry_file_name
    exec_cmd_orig = manage_composable.exec_cmd_info

    try:
        manage_composable.exec_cmd_info = \
            Mock(return_value='INFO:cadc-data:info\n'
                              'File C170324_0054_SCI_prev.jpg:\n'
                              '    archive: OMM\n'
                              '   encoding: None\n'
                              '    lastmod: Mon, 25 Jun 2018 16:52:07 GMT\n'
                              '     md5sum: f37d21c53055498d1b5cb7753e1c6d6f\n'
                              '       name: C120902_sh2-132_J_old_SCIRED.fits.gz\n'
                              '       size: 754408\n'
                              '       type: image/jpeg\n'
                              '    umd5sum: 704b494a972eed30b18b817e243ced7d\n'
                              '      usize: 754408\n'.encode('utf-8'))

        test_config.task_types = [manage_composable.TaskType.SCRAPE]
        test_oe = omm_composable.OrganizeExecutes(test_config)
        executors = test_oe.choose(test_obs_id)
        assert executors is not None
        assert len(executors) == 1
        assert isinstance(executors[0], omm_composable.Omm2Caom2Scrape)

        test_config.task_types = [manage_composable.TaskType.STORE,
                                  manage_composable.TaskType.INGEST,
                                  manage_composable.TaskType.MODIFY]
        test_oe = omm_composable.OrganizeExecutes(test_config)
        executors = test_oe.choose(test_obs_id)
        assert executors is not None
        assert len(executors) == 4
        assert isinstance(executors[0], omm_composable.Omm2Caom2Store)
        assert isinstance(executors[1], omm_composable.Omm2Caom2LocalMeta)
        assert isinstance(executors[2], omm_composable.Omm2Caom2LocalData)
        assert isinstance(executors[3], omm_composable.Omm2Caom2CompareChecksum)

        test_config.use_local_files = False
        test_config.task_types = [manage_composable.TaskType.INGEST,
                                  manage_composable.TaskType.MODIFY]
        test_oe = omm_composable.OrganizeExecutes(test_config)
        executors = test_oe.choose(test_obs_id)
        assert executors is not None
        assert len(executors) == 2
        assert isinstance(executors[0], omm_composable.Omm2Caom2Meta)
        assert isinstance(executors[1], omm_composable.Omm2Caom2Data)

        test_config.task_types = [manage_composable.TaskType.SCRAPE,
                                  manage_composable.TaskType.MODIFY]
        test_config.use_local_files = True
        test_oe = omm_composable.OrganizeExecutes(test_config)
        executors = test_oe.choose(test_obs_id)
        assert executors is not None
        assert len(executors) == 2
        assert isinstance(executors[0], omm_composable.Omm2Caom2Scrape)
        assert isinstance(executors[1], omm_composable.Omm2Caom2DataScrape)
    finally:
        manage_composable.exec_cmd_orig = exec_cmd_orig


def test_organize_executes_client():
    test_obs_id = 'Ctest_obs_id_SCI'
    test_config = _init_config()
    test_config.use_local_files = True
    test_config.proxy = 'abc'
    test_config.resource_id = 'ivo://cadc.nrc.ca/sc2tap'
    log_file_directory = os.path.join(THIS_DIR, 'logs')
    test_config.log_file_directory = log_file_directory
    success_log_file_name = 'success_log.txt'
    test_config.success_log_file_name = success_log_file_name
    failure_log_file_name = 'failure_log.txt'
    test_config.failure_log_file_name = failure_log_file_name
    retry_file_name = 'retries.txt'
    test_config.retry_file_name = retry_file_name
    exec_cmd_orig = manage_composable.exec_cmd_info
    subject_orig = net.Subject
    cadc_client_orig = cadcdata.CadcDataClient
    caom_client_orig = caom2repo.CAOM2RepoClient
    try:
        net.Subject = Mock()
        cadcdata.CadcDataClient = Mock()
        caom2repo.CAOM2RepoClient = Mock()

        manage_composable.exec_cmd_info = \
            Mock(return_value='INFO:cadc-data:info\n'
                              'File C170324_0054_SCI_prev.jpg:\n'
                              '    archive: OMM\n'
                              '   encoding: None\n'
                              '    lastmod: Mon, 25 Jun 2018 16:52:07 GMT\n'
                              '     md5sum: f37d21c53055498d1b5cb7753e1c6d6f\n'
                              '       name: C120902_sh2-132_J_old_SCIRED.fits.gz\n'
                              '       size: 754408\n'
                              '       type: image/jpeg\n'
                              '    umd5sum: 704b494a972eed30b18b817e243ced7d\n'
                              '      usize: 754408\n'.encode('utf-8'))

        test_config.task_types = [manage_composable.TaskType.SCRAPE]
        test_oe = omm_composable.OrganizeExecutes(test_config)
        executors = test_oe.choose_client(test_obs_id)
        assert executors is not None
        assert len(executors) == 1
        assert isinstance(executors[0], omm_composable.Omm2Caom2Scrape)

        test_config.task_types = [manage_composable.TaskType.STORE,
                                  manage_composable.TaskType.INGEST,
                                  manage_composable.TaskType.MODIFY]
        test_oe = omm_composable.OrganizeExecutes(test_config)
        executors = test_oe.choose_client(test_obs_id)
        assert executors is not None
        assert len(executors) == 4
        import logging
        logging.error(executors)
        assert isinstance(executors[0], omm_composable.Omm2Caom2StoreClient)
        assert isinstance(executors[1], omm_composable.Omm2Caom2LocalMetaClient)
        assert isinstance(executors[2], omm_composable.Omm2Caom2LocalDataClient)
        assert isinstance(executors[3],
                          omm_composable.Omm2Caom2CompareChecksumClient)

        test_config.use_local_files = False
        test_config.task_types = [manage_composable.TaskType.INGEST,
                                  manage_composable.TaskType.MODIFY]
        test_oe = omm_composable.OrganizeExecutes(test_config)
        executors = test_oe.choose_client(test_obs_id)
        assert executors is not None
        assert len(executors) == 2
        assert isinstance(executors[0], omm_composable.Omm2Caom2MetaClient)
        assert isinstance(executors[1], omm_composable.Omm2Caom2DataClient)

        test_config.task_types = [manage_composable.TaskType.SCRAPE,
                                  manage_composable.TaskType.MODIFY]
        test_config.use_local_files = True
        test_oe = omm_composable.OrganizeExecutes(test_config)
        executors = test_oe.choose_client(test_obs_id)
        assert executors is not None
        assert len(executors) == 2
        assert isinstance(executors[0], omm_composable.Omm2Caom2Scrape)
        assert isinstance(executors[1], omm_composable.Omm2Caom2DataScrape)
    finally:
        manage_composable.exec_cmd_orig = exec_cmd_orig
        net.Subject = subject_orig
        cadcdata.CadcDataClient = cadc_client_orig
        caom2repo.CAOM2RepoClient = caom_client_orig


def test_data_cmd_info():
    exec_cmd_orig = manage_composable.exec_cmd_info
    try:
        manage_composable.exec_cmd_info = \
            Mock(return_value='INFO:cadc-data:info\n'
                              'File C170324_0054_SCI_prev.jpg:\n'
                              '    archive: OMM\n'
                              '   encoding: None\n'
                              '    lastmod: Mon, 25 Jun 2018 16:52:07 GMT\n'
                              '     md5sum: f37d21c53055498d1b5cb7753e1c6d6f\n'
                              '       name: C120902_sh2-132_J_old_SCIRED.fits.gz\n'
                              '       size: 754408\n'
                              '       type: image/jpeg\n'
                              '    umd5sum: 704b494a972eed30b18b817e243ced7d\n'
                              '      usize: 754408\n')
        test_config = _init_config()
        test_obs_id = 'TEST_OBS_ID'
        test_executor = omm_composable.Omm2Caom2Meta(test_config, test_obs_id)
        test_executor._find_file_name_storage()
        assert test_executor.fname is not None, test_executor.fname
        assert test_executor.fname == 'C120902_sh2-132_J_old_SCIRED.fits.gz', \
            test_executor.fname
        assert manage_composable.exec_cmd_info.called
    finally:
        manage_composable.exec_cmd_orig = exec_cmd_orig


def test_capture_failure():
    test_obs_id = 'test_obs_id'
    test_config = _init_config()
    log_file_directory = os.path.join(THIS_DIR, 'logs')
    test_config.log_to_file = True
    test_config.log_file_directory = log_file_directory
    success_log_file_name = 'success_log.txt'
    test_config.success_log_file_name = success_log_file_name
    failure_log_file_name = 'failure_log.txt'
    test_config.failure_log_file_name = failure_log_file_name
    retry_file_name = 'retries.txt'
    test_config.retry_file_name = retry_file_name

    # success = test_config.success_fqn
    # failure = os.path.join(log_file_directory, failure_log_file_name)
    # retry = os.path.join(log_file_directory, retry_file_name)

    if not os.path.exists(log_file_directory):
        os.mkdir(log_file_directory)
    if os.path.exists(test_config.success_fqn):
        os.remove(test_config.success_fqn)
    if os.path.exists(test_config.failure_fqn):
        os.remove(test_config.failure_fqn)
    if os.path.exists(test_config.retry_fqn):
        os.remove(test_config.retry_fqn)

    # clean up from last execution

    test_oe = omm_composable.OrganizeExecutes(test_config)
    test_oe.capture_failure(test_obs_id, None, 'exception text')
    test_oe.capture_success(test_obs_id, 'C121212_01234_CAL.fits.gz')

    assert os.path.exists(test_config.success_fqn)
    assert os.path.exists(test_config.failure_fqn)
    assert os.path.exists(test_config.retry_fqn)


def _communicate():
    # return ['return status', None]
    return ['return status', None]


def _get_headers(uri, subject):
    x = """SIMPLE  =                    T / Written by IDL:  Fri Oct  6 01:48:35 2017      
BITPIX  =                  -32 / Bits per pixel                                 
NAXIS   =                    2 / Number of dimensions                           
NAXIS1  =                 2048 /                                                
NAXIS2  =                 2048 /                                                
DATATYPE= 'REDUC   '           /Data type, SCIENCE/CALIB/REJECT/FOCUS/TEST
END
"""
    delim = '\nEND'
    extensions = \
        [e + delim for e in x.split(delim) if e.strip()]
    headers = [fits.Header.fromstring(e, sep='\n') for e in extensions]
    return headers


def _get_test_metadata(subject, path):
    return {'size': 37,
            'md5sum': 'e330482de75d5c4c88ce6f6ef99035ea',
            'type': 'applicaton/octect-stream'}


def _get_test_file_meta(path):
    return _get_test_metadata(None, None)


def _read_obs(arg1):
    return SimpleObservation(collection='test_collection',
                             observation_id='test_obs_id',
                             algorithm=Algorithm(str('exposure')))


def _get_file_headers(fname):
    return _get_headers(None, None)


def _get_fname():
    return 'TBD'
